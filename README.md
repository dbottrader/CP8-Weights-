---
language:
- en
license: mit
library_name: transformers
pipeline_tag: text-generation
base_model:
- openai-community/gpt2
tags:
- asin-hhc
- cp8
- gpt2
- safetensors
- geometric-intelligence
- seed-checkpoint
---

# CP8 Weights — GPT-2 124M Seed Checkpoint

This repository is the public checkpoint home for the ASIN-HHC / CP8 model line led by **Dennis M. Christie (CP8)**.

## Current release

`CP8-GPT2-124M-Seed-v0.1` is a real Hugging Face-loadable checkpoint containing:

- pretrained GPT-2 base weights;
- a deterministic 1,024-token CP8 glyph/protocol bank;
- SafeTensors shards kept below GitHub's 100 MB per-file limit;
- tokenizer files and CP8 token registry;
- SHA-256 manifest;
- a reproducible GitHub Actions build;
- a local load and forward-pass verification script.

The base is deliberately **not instruction-tuned**. It is intended as a minimally steered foundation for later CP8 corpus training and LoRA adaptation.

## Status boundary

The inherited GPT-2 weights are pretrained. The newly added CP8 token embeddings are deterministically initialized but are **not yet CP8-corpus-trained**. This seed checkpoint does not claim to be the missing historical CP8 experimental checkpoint or to independently establish earlier emergence claims.

That distinction is recorded in `MODEL_STATUS.json` and enforced by the manifest and build workflow.

## Automatic build

GitHub Actions runs `scripts/build_cp8_checkpoint.py`, downloads the GPT-2 base, adds the CP8 token bank, saves sharded SafeTensors, verifies the package, and commits the generated model files to `main`.

## Load with Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

repo = "dbottrader/CP8-Weights-"
tokenizer = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo)

inputs = tokenizer("<CP8_ASIN><CP8_HHC><CP8_CP8>", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```

## Verify a clone

```bash
pip install -r requirements.txt
python scripts/verify_checkpoint.py
```

## Next promotion gate

The next release should train the CP8 bank and/or LoRA adapters against a frozen, versioned CP8 corpus and publish:

- dataset manifest and licenses;
- exact training configuration and seeds;
- adapter or merged checkpoint files;
- loss/evaluation records;
- independent reproduction receipt.

## Governance

- Capability does not imply authority.
- No receipt means no promotion.
- Replay supersedes narration.
- Specification is not implementation.
- Reality retains veto.

## Authorship

Primary project architect: **Dennis M. Christie (CP8)**. Tool and collaborator contributions must be credited at the artifact level.
