from __future__ import annotations
from collections import defaultdict


def distribute_round_robin(cases: list[dict], professionals: list[dict]) -> list[dict]:
    if not professionals:
        raise ValueError("Nenhum profissional configurado para distribuição.")
    loads=defaultdict(int)
    ordered=sorted(cases,key=lambda x:(-int(x.get('reassessment',False)),-int(x.get('complexity_rank',0)),str(x.get('grr',''))))
    out=[]
    for case in ordered:
        prof=min(professionals,key=lambda p:(loads[p['id']],p['id']))
        loads[prof['id']]+=1
        out.append({**case,'professional_id':prof['id']})
    return out
