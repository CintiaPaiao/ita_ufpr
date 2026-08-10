from dataclasses import dataclass
from typing import Optional, Sequence
from src.domain.mcn.rules import art19_limit
from src.config.settings import IAL_CONFIG
def clamp(x,lo=0,hi=1):return max(lo,min(hi,x))
def rendimento_component(aprovacao_atual_pct,aprovacao_historica_pct=None):
    if aprovacao_atual_pct is None:return None
    base=1-aprovacao_atual_pct/100
    if aprovacao_historica_pct is None:return clamp(base)
    trend=clamp((aprovacao_historica_pct-aprovacao_atual_pct)/IAL_CONFIG['parameters']['trend_reference_pp'],-1,1)
    return clamp(base+IAL_CONFIG['parameters']['trend_modifier']*trend)
def frequencia_component(n_disciplinas,rep_freq_atual,historico_taxas=None):
    if n_disciplinas is None or rep_freq_atual is None or n_disciplinas<=0:return None
    taxa=rep_freq_atual/n_disciplinas; lim=art19_limit(n_disciplinas); exc=max(0,rep_freq_atual-lim)/max(1,n_disciplinas-lim); atual=.65*taxa+.35*exc
    hist=[x for x in (historico_taxas or []) if x is not None]
    return clamp(atual if not hist else .75*atual+.25*(sum(hist[-3:])/len(hist[-3:])))
def progressao_component(ch_integralizada,ch_total,periodos_efetivos,periodos_regulares,ritmo_recente=None):
    if None in (ch_integralizada,ch_total,periodos_efetivos,periodos_regulares) or ch_total<=0 or periodos_regulares<=0:return None
    esperado=min(1,periodos_efetivos/periodos_regulares); observado=ch_integralizada/ch_total; gap=max(0,esperado-observado); sev=min(1,gap/IAL_CONFIG['parameters']['progress_gap_reference'])
    if ritmo_recente is None:return clamp(sev)
    return clamp(.75*sev+.25*(1-min(1,ritmo_recente)))
def classify_band(score):
    if score is None:return None
    for b in IAL_CONFIG['bands']:
        if b['min']<=score<=b['max']:return b['label']
@dataclass
class IALCalculation:r:Optional[float];f:Optional[float];p:Optional[float];score:Optional[float];coverage:float;status:str;band:Optional[str]
def calculate_ial(r,f,p):
    w=IAL_CONFIG['weights']; pairs=[(w['rendimento'],r),(w['frequencia'],f),(w['progressao'],p)]; a=[(float(x),y) for x,y in pairs if y is not None]; cov=sum(x for x,_ in a)
    if cov<IAL_CONFIG['coverage']['partial_minimum']:return IALCalculation(r,f,p,None,cov,'NAO_CALCULAVEL',None)
    score=sum(x*y for x,y in a)/cov*100; status='COMPLETO' if cov>=100 else 'IAL PARCIAL – REQUER CONFERÊNCIA'; return IALCalculation(r,f,p,score,cov,status,classify_band(score))
