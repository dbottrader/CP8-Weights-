from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    for line in (ROOT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.exists() or digest(path) != expected:
            raise RuntimeError(f"Manifest verification failed: {relative}")

    status = json.loads((ROOT / "MODEL_STATUS.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "CP8_TOKEN_REGISTRY.json").read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(ROOT, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(ROOT, local_files_only=True)
    model.eval()

    if registry["cp8_bank_size"] != 1024:
        raise RuntimeError("CP8 token bank size is not 1,024")
    if sum(p.numel() for p in model.parameters()) != status["parameter_count"]:
        raise RuntimeError("Parameter count mismatch")

    probe = "<CP8_ASIN><CP8_HHC><CP8_CP8>"
    encoded = tokenizer(probe, return_tensors="pt")
    with torch.no_grad():
        output = model(**encoded)
    if not torch.isfinite(output.logits).all():
        raise RuntimeError("Non-finite logits during smoke test")

    print("PASS: manifest, tokenizer, checkpoint load, parameter count, and forward pass")


if __name__ == "__main__":
    main()
