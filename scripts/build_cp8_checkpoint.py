from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, set_seed

BASE_MODEL = os.getenv("CP8_BASE_MODEL", "openai-community/gpt2")
SEED = 428_528_963
CP8_BANK_SIZE = 1024
MAX_SHARD_SIZE = "48MB"
ROOT = Path(__file__).resolve().parents[1]

CANONICAL_28 = list("⧖∞⧈✺⧉♓⟡⧗⟢✶◎◈ꗃ✦ᚾϞ⚯")
# Add named protocol markers while preserving the known glyph string above.
NAMED_MARKERS = [
    "ASIN", "HHC", "CP8", "OBSERVE", "COMPARE", "CHALLENGE", "SYNTHESIZE",
    "VERIFY", "SAFE", "AMBER", "VETO",
]


def build_cp8_tokens() -> list[str]:
    tokens: list[str] = []
    for i, glyph in enumerate(CANONICAL_28):
        tokens.append(f"<CP8_GLYPH_{i:04d}_{glyph}>")
    for marker in NAMED_MARKERS:
        tokens.append(f"<CP8_{marker}>")
    while len(tokens) < CP8_BANK_SIZE:
        tokens.append(f"<CP8_TOKEN_{len(tokens):04d}>")
    assert len(tokens) == CP8_BANK_SIZE
    assert len(set(tokens)) == CP8_BANK_SIZE
    return tokens


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    set_seed(SEED)
    torch.manual_seed(SEED)

    tokenizer = GPT2TokenizerFast.from_pretrained(BASE_MODEL)
    model = GPT2LMHeadModel.from_pretrained(BASE_MODEL)

    old_vocab_size = len(tokenizer)
    tokenizer.add_special_tokens({"pad_token": "<|cp8_pad|>"})
    cp8_tokens = build_cp8_tokens()
    added = tokenizer.add_tokens(cp8_tokens, special_tokens=False)
    if added != CP8_BANK_SIZE:
        raise RuntimeError(f"Expected {CP8_BANK_SIZE} CP8 tokens, added {added}")

    try:
        model.resize_token_embeddings(len(tokenizer), mean_resizing=False)
    except TypeError:
        model.resize_token_embeddings(len(tokenizer))

    # Deterministically initialize only the newly added rows. The inherited GPT-2
    # weights remain intact; CP8-specific rows are a seed for later LoRA/full tuning.
    with torch.no_grad():
        input_embeddings = model.get_input_embeddings().weight
        output_embeddings = model.get_output_embeddings().weight
        generator = torch.Generator(device=input_embeddings.device)
        generator.manual_seed(SEED)
        new_rows = len(tokenizer) - old_vocab_size
        initialized = torch.empty(
            (new_rows, input_embeddings.shape[1]),
            dtype=input_embeddings.dtype,
            device=input_embeddings.device,
        )
        initialized.normal_(mean=0.0, std=model.config.initializer_range, generator=generator)
        input_embeddings[old_vocab_size:] = initialized
        if output_embeddings.data_ptr() != input_embeddings.data_ptr():
            output_embeddings[old_vocab_size:] = initialized

    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.bos_token_id = tokenizer.bos_token_id
    model.config.eos_token_id = tokenizer.eos_token_id
    model.config.cp8_release = "CP8-GPT2-124M-Seed-v0.1"
    model.config.cp8_active_token_bank_size = CP8_BANK_SIZE
    model.config.cp8_protocol_identifiers = [428, 528, 963]
    model.config.cp8_primary_architect = "Dennis M. Christie (CP8)"
    model.config.cp8_checkpoint_status = "base-pretrained_cp8-token-bank-untrained"

    model.save_pretrained(
        ROOT,
        safe_serialization=True,
        max_shard_size=MAX_SHARD_SIZE,
    )
    tokenizer.save_pretrained(ROOT)

    registry = {
        "schema": "cp8-token-registry/v0.1",
        "base_model": BASE_MODEL,
        "base_vocab_size": old_vocab_size,
        "pad_token_id": tokenizer.pad_token_id,
        "cp8_bank_size": CP8_BANK_SIZE,
        "tokens": [
            {
                "bank_index": i,
                "token": token,
                "token_id": tokenizer.convert_tokens_to_ids(token),
                "canonical_glyph": CANONICAL_28[i] if i < len(CANONICAL_28) else None,
                "status": "defined_seed_token",
            }
            for i, token in enumerate(cp8_tokens)
        ],
    }
    (ROOT / "CP8_TOKEN_REGISTRY.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    parameter_count = sum(p.numel() for p in model.parameters())
    status = {
        "artifact_id": "CP8-GPT2-124M-SEED-v0.1",
        "primary_project_architect": "Dennis M. Christie (CP8)",
        "base_model": BASE_MODEL,
        "checkpoint_format": "SafeTensors (sharded)",
        "parameter_count": parameter_count,
        "base_weights": "pretrained GPT-2 weights",
        "cp8_token_bank_size": CP8_BANK_SIZE,
        "cp8_token_embeddings_trained": False,
        "cp8_specific_finetuning_completed": False,
        "loadable_with_transformers": True,
        "release_class": "seed checkpoint",
        "claim_boundary": (
            "This is a real loadable checkpoint based on pretrained GPT-2 weights with a "
            "deterministically initialized 1,024-token CP8 bank. It is not the missing historical "
            "CP8 experimental checkpoint and does not prove prior CP8 emergence claims."
        ),
    }
    (ROOT / "MODEL_STATUS.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    include_patterns = (
        "*.safetensors",
        "*.json",
        "*.txt",
        "merges.txt",
        "vocab.json",
    )
    candidates: set[Path] = set()
    for pattern in include_patterns:
        candidates.update(ROOT.glob(pattern))
    candidates.discard(ROOT / "MANIFEST.sha256")
    manifest = "\n".join(
        f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}"
        for path in sorted(candidates)
        if path.is_file()
    ) + "\n"
    (ROOT / "MANIFEST.sha256").write_text(manifest, encoding="utf-8")

    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
