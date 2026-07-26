from __future__ import annotations
import argparse, csv, hashlib, json, math, os, random, time
from dataclasses import dataclass, asdict
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from safetensors.torch import save_file

@dataclass
class Config:
    vocab_size: int = 256
    context_length: int = 192
    d_model: int = 384
    n_heads: int = 8
    n_layers: int = 8
    d_ff: int = 1536
    dropout: float = 0.0
    seed: int = 428

class CausalSelfAttention(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        assert c.d_model % c.n_heads == 0
        self.n_heads=c.n_heads
        self.head_dim=c.d_model//c.n_heads
        self.qkv=nn.Linear(c.d_model,3*c.d_model,bias=False)
        self.proj=nn.Linear(c.d_model,c.d_model,bias=False)
        self.dropout=c.dropout
    def forward(self,x):
        B,T,C=x.shape
        q,k,v=self.qkv(x).chunk(3,dim=-1)
        q=q.view(B,T,self.n_heads,self.head_dim).transpose(1,2)
        k=k.view(B,T,self.n_heads,self.head_dim).transpose(1,2)
        v=v.view(B,T,self.n_heads,self.head_dim).transpose(1,2)
        y=F.scaled_dot_product_attention(q,k,v,is_causal=True,dropout_p=self.dropout if self.training else 0.0)
        y=y.transpose(1,2).contiguous().view(B,T,C)
        return self.proj(y)

class Block(nn.Module):
    def __init__(self,c:Config):
        super().__init__()
        self.ln1=nn.LayerNorm(c.d_model)
        self.attn=CausalSelfAttention(c)
        self.ln2=nn.LayerNorm(c.d_model)
        self.mlp=nn.Sequential(nn.Linear(c.d_model,c.d_ff),nn.GELU(),nn.Linear(c.d_ff,c.d_model))
    def forward(self,x):
        x=x+self.attn(self.ln1(x))
        x=x+self.mlp(self.ln2(x))
        return x

class RecoveryGPT(nn.Module):
    def __init__(self,c:Config):
        super().__init__(); self.c=c
        self.tok=nn.Embedding(c.vocab_size,c.d_model)
        self.pos=nn.Embedding(c.context_length,c.d_model)
        self.blocks=nn.ModuleList([Block(c) for _ in range(c.n_layers)])
        self.ln=nn.LayerNorm(c.d_model)
        self.head=nn.Linear(c.d_model,c.vocab_size,bias=False)
        self.head.weight=self.tok.weight
        self.apply(self._init)
    def _init(self,m):
        if isinstance(m,(nn.Linear,nn.Embedding)): nn.init.normal_(m.weight,mean=0,std=0.02)
        if isinstance(m,nn.Linear) and m.bias is not None: nn.init.zeros_(m.bias)
    def forward(self,idx,targets=None):
        B,T=idx.shape
        x=self.tok(idx)+self.pos(torch.arange(T,device=idx.device))[None,:,:]
        for b in self.blocks: x=b(x)
        logits=self.head(self.ln(x))
        loss=None
        if targets is not None: loss=F.cross_entropy(logits.reshape(-1,logits.size(-1)),targets.reshape(-1))
        return logits,loss

@torch.no_grad()
def generate(model,prompt:bytes,max_new=300,temp=0.8):
    device=next(model.parameters()).device
    idx=torch.tensor(list(prompt),dtype=torch.long,device=device)[None,:]
    for _ in range(max_new):
        crop=idx[:,-model.c.context_length:]
        logits,_=model(crop)
        probs=F.softmax(logits[:,-1,:]/temp,dim=-1)
        nxt=torch.multinomial(probs,1)
        idx=torch.cat([idx,nxt],dim=1)
    return bytes(idx[0].tolist()).decode('utf-8',errors='replace')

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--steps',type=int,default=120)
    ap.add_argument('--batch-size',type=int,default=4)
    ap.add_argument('--lr',type=float,default=3e-4)
    args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    c=Config()
    random.seed(c.seed); torch.manual_seed(c.seed); torch.set_num_threads(max(1,min(8,os.cpu_count() or 1)))
    data=Path(args.corpus).read_bytes()
    if len(data)<c.context_length+2: raise ValueError('corpus too small')
    model=RecoveryGPT(c)
    opt=torch.optim.AdamW(model.parameters(),lr=args.lr,betas=(0.9,0.95),weight_decay=0.1)
    n_params=sum(p.numel() for p in model.parameters())
    log=[]; start=time.time()
    model.train()
    for step in range(1,args.steps+1):
        starts=[random.randint(0,len(data)-c.context_length-2) for _ in range(args.batch_size)]
        x=torch.stack([torch.tensor(list(data[s:s+c.context_length]),dtype=torch.long) for s in starts])
        y=torch.stack([torch.tensor(list(data[s+1:s+c.context_length+1]),dtype=torch.long) for s in starts])
        _,loss=model(x,y)
        opt.zero_grad(set_to_none=True); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        elapsed=time.time()-start
        log.append({'step':step,'loss':float(loss.item()),'elapsed_s':elapsed})
        if step==1 or step%10==0 or step==args.steps:
            print(f'step={step} loss={loss.item():.4f} elapsed={elapsed:.1f}s',flush=True)
    model.eval()
    state={k:v.detach().cpu().contiguous() for k,v in model.state_dict().items()}
    # tok.weight and head.weight are intentionally tied. Persist one canonical copy;
    # loaders reconstruct the tie from the model architecture before loading.
    state.pop('head.weight', None)
    weights=out/'model.safetensors'; save_file(state,str(weights),metadata={'format':'pt','artifact':'CP8-ACE-Recovery-Micro-v0.1','tied_weights':'head.weight=tok.weight'})
    cfg=asdict(c)|{'parameter_count':n_params,'architecture':'byte-level decoder-only transformer','training_steps':args.steps,'batch_size':args.batch_size,'learning_rate':args.lr}
    (out/'config.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    with (out/'training_log.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['step','loss','elapsed_s']);w.writeheader();w.writerows(log)
    sample=generate(model,b'<|instruction|>\nDefine CP8.\n<|response|>\n',max_new=400,temp=0.75)
    (out/'sample_generation.txt').write_text(sample,encoding='utf-8')
    status={
      'model_id':'CP8-ACE-Recovery-Micro-v0.1',
      'owner':'Dennis M. Christie / CP8',
      'historical_checkpoint_recovered':False,
      'is_original_124m_cp8':False,
      'is_newly_trained':True,
      'base_model':'none; trained from random initialization',
      'training_data':'redacted project recovery corpus plus canonical governance seed',
      'evidence_grade':'E1_LOCAL_BOOTSTRAP',
      'limitations':['micro-model, not production quality','not independently reproduced','raw recovery corpus requires manual public-release review'],
      'weights_sha256':sha256(weights),
      'corpus_sha256':sha256(Path(args.corpus)),
      'final_loss':log[-1]['loss'],
      'initial_loss':log[0]['loss'],
      'parameter_count':n_params,
    }
    (out/'MODEL_STATUS.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
if __name__=='__main__': main()
