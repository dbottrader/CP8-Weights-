# Model Card — CP8-ACE-Recovery-Micro-v0.1

## Model identity

- **Model ID:** `CP8-ACE-Recovery-Micro-v0.1`
- **Steward:** Dennis M. Christie / CP8
- **Release date:** 2026-07-26
- **Evidence grade:** `E1_LOCAL_BOOTSTRAP`
- **Format:** SafeTensors
- **Base model:** none; deterministic random initialization

## Architecture

A compact byte-level decoder-only transformer:

- vocabulary: 256 byte values
- context length: 192
- embedding width: 384
- attention heads: 8
- transformer blocks: 8
- feed-forward width: 1,536
- tied token/output embeddings
- parameter count: 14,356,224
- initialization seed: 428

## Training

- optimizer: AdamW
- learning rate: 0.0003
- batch size: 4
- training steps: 80
- initial recorded loss: 5.468018054962158
- final recorded loss: 3.022549867630005

The private training input was a project-focused recovery corpus assembled from preserved ACE, ASIN-HHC, CP8, HOS, glyph, governance, wallet, PoWP, OpenAI, Gemini, and Kimi materials. Credentials, obvious direct identifiers, and unrelated material were filtered programmatically. The corpus remains private pending human review.

The repository includes a small public canonical instruction seed for governance and architecture vocabulary. It is not sufficient by itself to reproduce the published checkpoint hash.

## Verification

The saved checkpoint was loaded into the declared architecture and completed a finite-logit forward pass. Tied embeddings were restored successfully.

- checkpoint load: PASS
- forward pass: PASS
- finite logits: PASS
- tied weights restored: PASS
- weights SHA-256: `11297bcb6bd88f3f1436be063efd30711b01258c849e6b1f40cdcb4f71795305`

## Intended use

This checkpoint is intended for:

- provenance and model-release workflow testing
- continued CP8 corpus curation
- deterministic loader and evaluation development
- small-scale research into sovereign-agent vocabulary and governance conditioning
- independent reproduction experiments using an approved public corpus

## Out-of-scope use

Do not treat this model as:

- the missing historical 124M CP8 checkpoint
- a production assistant
- a medical, legal, financial, or safety authority
- evidence of consciousness, scientific frequency effects, or physical performance
- a secure autonomous-agent runtime
- a financial token, settlement layer, or investment product

## Known limitations

- only 80 optimization steps
- no held-out benchmark suite yet
- byte-level vocabulary is inefficient for long-form generation
- no instruction-tuning evaluation
- no red-team or safety evaluation
- no independent reproduction receipt
- private corpus cannot currently be redistributed

## Promotion requirements

Promotion beyond E1 requires a frozen public dataset, exact environment specification, deterministic training configuration, held-out evaluation, signed artifact hashes, and at least one independent reproduction receipt.
