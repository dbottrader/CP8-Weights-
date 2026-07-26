---
language:
- en
license: mit
library_name: pytorch
pipeline_tag: text-generation
tags:
- asin-hhc
- cp8
- ace
- sovereign-agent
- provenance
- safetensors
- receipt-driven-ai
---

# CP8 Weights — ACE / ASIN-HHC Recovery Line

This repository is the public model and reproducibility surface for the **ACE / ASIN-HHC / CP8** research ecosystem led by **Dennis M. Christie (CP8)**.

## Current verified release

### `CP8-ACE-Recovery-Micro-v0.1`

A newly trained, deterministic bootstrap checkpoint built from a private, redacted project-recovery corpus and a public canonical governance seed.

| Field | Verified value |
|---|---:|
| Architecture | byte-level decoder-only transformer |
| Parameters | 14,356,224 |
| Context length | 192 bytes |
| Training steps | 80 |
| Initial loss | 5.468018 |
| Final loss | 3.022550 |
| Checkpoint format | SafeTensors |
| Checkpoint size | 57,432,504 bytes |
| Weight SHA-256 | `11297bcb6bd88f3f1436be063efd30711b01258c849e6b1f40cdcb4f71795305` |
| Local verification | load + forward pass PASS |
| Evidence grade | `E1_LOCAL_BOOTSTRAP` |

## Evidence boundary

This release is **not** the unrecovered historical 124M CP8 checkpoint. It is a new reconstruction lineage with its own identifier, configuration, hashes, and receipts.

It is not production-ready, independently reproduced, safety-certified, or an authority-bearing system. The recovered private corpus is intentionally withheld pending human privacy, consent, and redistribution review.

## Start here

- [`MODEL_CARD.md`](./MODEL_CARD.md) — architecture, training, intended use, and limitations
- [`PROVENANCE.md`](./PROVENANCE.md) — artifact lineage and hashes
- [`PUBLICATION_BOUNDARY.md`](./PUBLICATION_BOUNDARY.md) — what is and is not public
- [`TOKEN_ECOSYSTEM.md`](./TOKEN_ECOSYSTEM.md) — HHC / PoWP / node ecosystem boundary
- [`COLLABORATION.md`](./COLLABORATION.md) — open roles and contribution workflow
- [`release/CP8-ACE-Recovery-Micro-v0.1/`](./release/CP8-ACE-Recovery-Micro-v0.1/) — verified release metadata
- [`scripts/`](./scripts/) — deterministic training and verification code

## Large files

The checkpoint and complete recovery archive are stored in the release archive folder because the public repository intentionally avoids committing private recovery corpora and oversized binary bundles through the normal GitHub contents path.

- Drive release folder: `https://drive.google.com/drive/folders/1h64tOSvTWnkaZ2pgGJBdJ6CYqrOWoub1`
- Checkpoint file ID: `1x1-sVw6NaOZ4tcB_W96E0r29lQvVxg9q`
- Recovery ZIP file ID: `1p0ZP-B-Wmn07u-SF-dNxLDagEyoJRw0n`

Verify every downloaded checkpoint against the SHA-256 above. Drive link visibility is controlled by the project steward.

## Constitutional rules

- No mechanism may silently convert uncertainty into authority.
- Capability does not imply authority.
- No receipt means no promotion.
- Replay supersedes narration.
- Specification is not implementation.
- Reality retains veto.

## Ecosystem map

```text
ACE human-facing sovereign agent interface
        ↓
ASIN intent and artifact grammar
        ↓
CP8 provenance, critique, replay, and promotion gates
        ↓
HOS / HarmonyOS interface and runtime lineage
        ↓
PoWP signed receipts and HHC internal contribution credits
        ↓
independent reproduction and community nodes
```

## Status

`PUBLIC_RESEARCH_RELEASE / E1_LOCAL_BOOTSTRAP / INDEPENDENT_REPRODUCTION_WANTED`

Primary architect and steward: **Dennis M. Christie (CP8)**.
