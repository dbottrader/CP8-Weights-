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

This repository is the public model, provenance, and collaboration surface for the **ACE / ASIN-HHC / CP8 / HOS** research ecosystem led by **Dennis M. Christie (CP8)**.

## Current verified checkpoint

### `CP8-ACE-Recovery-Micro-v0.1`

A newly trained deterministic bootstrap checkpoint built from a privacy-redacted project-recovery corpus and a canonical governance seed.

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

## Historical checkpoint boundary

This release is **not** the unrecovered historical 124M CP8 checkpoint. The historical experiment is documented, but its exact binary, source path, and original hash remain unrecovered. This checkpoint is a new reconstruction lineage with its own identity and receipts.

It is not production-ready, independently reproduced, safety-certified, or authority-bearing.

## Project-complete public source record

Project material is not withheld merely because it originated in a private chat. A privacy-reviewed public package preserves:

- 107 project conversations from the 2025 OpenAI export
- 4,842 message-level records
- derived public training text
- Gemini Gem project configuration
- Kimi project-session metadata
- sanitization, training, and verification scripts
- model, corpus, and package manifests

Only unrelated or sensitive personal data is removed or replaced. See [`CHAT_CORPUS.md`](./CHAT_CORPUS.md) and [`PUBLICATION_BOUNDARY.md`](./PUBLICATION_BOUNDARY.md).

Public source ZIP SHA-256:

`94b27c3912e38262045ca5841a5b4e53cb0024c89ccf1bece52e0ff43e16d986`

## Start here

- [`MODEL_CARD.md`](./MODEL_CARD.md) — architecture, training, intended use, and limitations
- [`PROVENANCE.md`](./PROVENANCE.md) — historical and reconstructed artifact lineage
- [`CHAT_CORPUS.md`](./CHAT_CORPUS.md) — transcript counts, hashes, and source-package pointer
- [`PUBLICATION_BOUNDARY.md`](./PUBLICATION_BOUNDARY.md) — project-complete/privacy-minimal release policy
- [`TOKEN_ECOSYSTEM.md`](./TOKEN_ECOSYSTEM.md) — HHC / PoWP / node ecosystem boundary
- [`COLLABORATION.md`](./COLLABORATION.md) — open roles and contribution workflow
- [`release/CP8-ACE-Recovery-Micro-v0.1/`](./release/CP8-ACE-Recovery-Micro-v0.1/) — verified checkpoint metadata
- [`release/ASIN-HHC-CP8-PUBLIC-SOURCE-20260726.json`](./release/ASIN-HHC-CP8-PUBLIC-SOURCE-20260726.json) — public source manifest
- [`scripts/`](./scripts/) — sanitization, training, and verification code

## Large-file archive

The checkpoint, complete recovery archive, and sanitized public source package are stored in the project release folder because the available GitHub connector accepts normal UTF-8 repository files but does not expose a binary-upload or Git-LFS path.

- Drive release folder: `https://drive.google.com/drive/folders/1h64tOSvTWnkaZ2pgGJBdJ6CYqrOWoub1`
- Checkpoint file ID: `1x1-sVw6NaOZ4tcB_W96E0r29lQvVxg9q`
- Full recovery ZIP file ID: `1p0ZP-B-Wmn07u-SF-dNxLDagEyoJRw0n`
- Sanitized public source ZIP file ID: `1VeQP_2EZVc9LXVwESmZtJY9iZ0RIa4SS`

Verify every download against the repository hashes. Drive visibility remains controlled by the project steward because the connected consumer-Gmail API cannot create anonymous link permissions.

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

`PUBLIC_RESEARCH_RELEASE / E1_LOCAL_BOOTSTRAP / PROJECT_SOURCE_HASHED / INDEPENDENT_REPRODUCTION_WANTED`

Primary architect and steward: **Dennis M. Christie (CP8)**.
