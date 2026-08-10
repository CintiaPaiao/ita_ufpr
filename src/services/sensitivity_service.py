from __future__ import annotations
from collections import Counter

SCENARIOS={
    "50/30/20":(50,30,20),
    "40/35/25":(40,35,25),
    "30/30/40":(30,30,40),
}

def _band(score):
    if score is None:return None
    if score<20:return "reduzida"
    if score<35:return "atenção"
    if score<50:return "relevante"
    if score<65:return "elevada"
    return "intensiva"

def analyze(records:list[dict]) -> dict:
    out={}
    for name,(wr,wf,wp) in SCENARIOS.items():
        vals=[]
        for x in records:
            comps=[(wr,x.get("r")),(wf,x.get("f")),(wp,x.get("p"))]
            avail=[(w,v) for w,v in comps if v is not None]
            cov=sum(w for w,_ in avail)
            score=None if cov<60 else sum(w*v for w,v in avail)/cov*100
            vals.append({"student_id":x.get("student_id"),"score":score,"faixa":_band(score)})
        out[name]={"records":vals,"bands":dict(Counter(v["faixa"] for v in vals if v["faixa"]))}
    return out
