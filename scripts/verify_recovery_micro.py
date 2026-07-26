from __future__ import annotations
import json, sys
from pathlib import Path
import torch
from safetensors.torch import load_file

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from train_recovery_micro import Config, RecoveryGPT

model_dir=ROOT/'release'/'CP8-ACE-Recovery-Micro-v0.1'
cfg_raw=json.loads((model_dir/'config.json').read_text())
cfg=Config(**{k:cfg_raw[k] for k in Config.__annotations__})
model=RecoveryGPT(cfg)
state=load_file(str(model_dir/'model.safetensors'))
missing,unexpected=model.load_state_dict(state,strict=False)
allowed_missing={'head.weight'}
if set(missing) != allowed_missing or unexpected:
    raise SystemExit(f'load mismatch: missing={missing}, unexpected={unexpected}')
# Reassert tied output head after loading canonical tok.weight.
model.head.weight=model.tok.weight
model.eval()
x=torch.tensor([[60,124,105,110,115,116,114,117,99,116,105,111,110,124,62]],dtype=torch.long)
with torch.no_grad():
    logits,loss=model(x,x)
assert logits.shape==(1,x.shape[1],cfg.vocab_size)
assert torch.isfinite(logits).all()
result={
    'verified': True,
    'checkpoint_load': 'PASS',
    'forward_pass': 'PASS',
    'logits_shape': list(logits.shape),
    'finite_logits': True,
    'tied_weights_restored': model.head.weight.data_ptr()==model.tok.weight.data_ptr(),
    'self_loss': float(loss.item()),
}
(model_dir/'VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
