from __future__ import annotations
import re, pandas as pd
def padronizar_grr(value):
    if value is None or (isinstance(value,float) and pd.isna(value)): return None
    s=str(value).strip().upper().replace(' ','')
    m=re.search(r'(?:GRR|TRR)?(\d{8})',s)
    if m: return ('TRR' if s.startswith('TRR') else 'GRR')+m.group(1)
    return s or None
def validar_grr(v): return bool(v and re.fullmatch(r'(GRR|TRR)\d{8}',v))
def normalize_dataframe_grr(df,col='GRR'):
    out=df.copy(); out[f'{col}_ORIGINAL']=out[col]; out[col]=out[col].map(padronizar_grr); return out
