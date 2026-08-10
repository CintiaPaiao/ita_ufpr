from dataclasses import dataclass
BAND={'Prioridade acadêmica intensiva':5,'Prioridade acadêmica elevada':4,'Prioridade acadêmica relevante':3,'Prioridade acadêmica de atenção':2,'Prioridade acadêmica reduzida':1,None:0}
@dataclass
class PriorityInput: grr:str; mcn_noncompliance_count:int=0; mcn_pending_count:int=0; ial_score:float|None=None; ial_band:str|None=None; reassessment:bool=False; longitudinal_worsening:bool=False; protective_priority:bool=False; intervention_need:bool=False; institutional_barrier:bool=False; near_completion:bool=False
@dataclass
class PriorityResult: grr:str; layer:str; reasons:list[str]; sort_key:tuple
def classify_layer(x):
    reasons=[]; hi=BAND.get(x.ial_band,0)>=4; rel=BAND.get(x.ial_band,0)>=3
    if x.mcn_noncompliance_count and hi:layer='A';reasons=['MCN sinalizada','IAL elevado/intensivo']
    elif x.reassessment and (x.mcn_noncompliance_count or x.longitudinal_worsening or rel):layer='B';reasons=['Reavaliação','recorrência/agravamento acadêmico']
    elif hi or x.longitudinal_worsening:layer='C';reasons=['comprometimento longitudinal']
    elif x.protective_priority or x.intervention_need or x.institutional_barrier:layer='D';reasons=['prioridade protetiva/interventiva']
    else:layer='E';reasons=['demais situações para análise']
    key=(-x.mcn_noncompliance_count,-BAND.get(x.ial_band,0),-(x.ial_score or -1),-int(x.longitudinal_worsening),-int(x.reassessment),-int(x.near_completion),x.grr)
    return PriorityResult(x.grr,layer,reasons,key)
def prioritize(items,n):
    order={'A':0,'B':1,'C':2,'D':3,'E':4}; r=[classify_layer(x) for x in items];r.sort(key=lambda z:(order[z.layer],z.sort_key));return r[:n]
