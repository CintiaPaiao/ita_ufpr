from __future__ import annotations
import os, re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def _expand(v):
    if isinstance(v,str):
        pat=re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")
        return pat.sub(lambda m: os.getenv(m.group(1),m.group(2) or ""),v)
    if isinstance(v,dict): return {k:_expand(x) for k,x in v.items()}
    if isinstance(v,list): return [_expand(x) for x in v]
    return v
def load_yaml(name):
    with open(ROOT/'configs'/name,encoding='utf-8') as f: return _expand(yaml.safe_load(f) or {})
APP_CONFIG=load_yaml('app.yaml'); IAL_CONFIG=load_yaml('ial.yaml'); MCN_CONFIG=load_yaml('mcn.yaml'); PRIORITY_CONFIG=load_yaml('priorizacao.yaml'); FEATURE_FLAGS=load_yaml('feature_flags.yaml').get('features',{})
