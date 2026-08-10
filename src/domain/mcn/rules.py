from dataclasses import dataclass
from typing import Optional, Iterable
from src.config.settings import MCN_CONFIG
@dataclass
class RuleResult:
    artigo:str; status:str; evidencia:dict; requer_conferencia:bool=False
def art19_limit(n:int)->int:
    return 0 if n<=2 else 1 if n<=4 else 2
def calcular_art17(mandatory_enrolled:Optional[bool],all_mandatory_completed:Optional[bool]):
    if mandatory_enrolled is None or all_mandatory_completed is None:return RuleResult('17','DADO_PENDENTE',{},True)
    if all_mandatory_completed:return RuleResult('17','NAO_SE_APLICA',{'todas_obrigatorias_cumpridas':True})
    return RuleResult('17','ATENDE' if mandatory_enrolled else 'NAO_ATENDE',{'obrigatoria_matriculada':mandatory_enrolled})
def calcular_art18(ch_matriculada:Optional[float],ch_minima:Optional[float],grau_evidencia:Optional[str]):
    if ch_matriculada is None:return RuleResult('18','DADO_PENDENTE',{},True)
    if ch_minima is None:return RuleResult('18','PARAMETRO_NAO_CONFIRMADO',{'ch_matriculada':ch_matriculada},True)
    if (grau_evidencia or 'D').upper()!=MCN_CONFIG['art18']['automatic_minimum_evidence_grade']:
        return RuleResult('18','REQUER_CONFERENCIA',{'ch_matriculada':ch_matriculada,'ch_minima':ch_minima,'grau_evidencia':grau_evidencia},True)
    return RuleResult('18','ATENDE' if ch_matriculada>=ch_minima else 'NAO_ATENDE',{'ch_matriculada':ch_matriculada,'ch_minima':ch_minima})
def calcular_art19(n_disciplinas:Optional[int],rep_freq:Optional[int]):
    if n_disciplinas is None or rep_freq is None:return RuleResult('19','DADO_PENDENTE',{},True)
    lim=art19_limit(n_disciplinas); return RuleResult('19','ATENDE' if rep_freq<=lim else 'NAO_ATENDE',{'n_disciplinas':n_disciplinas,'rep_freq':rep_freq,'limite':lim})
def calcular_art20(components:Iterable[dict],exclude_class_below_pct=50.0):
    eligible=[]; ec=et=0
    for c in components:
        if c.get('cancelado') is True:ec+=1;continue
        if c.get('taxa_turma') is not None and c.get('taxa_turma_validada',False) and c['taxa_turma']<exclude_class_below_pct:et+=1;continue
        eligible.append(c)
    if not eligible:return RuleResult('20','NAO_CALCULAVEL',{'elegiveis':0,'excluidos_cancelamento':ec,'excluidos_turma':et},True)
    ap=sum(c.get('aprovado') is True for c in eligible); pct=100*ap/len(eligible)
    return RuleResult('20','ATENDE' if pct>=MCN_CONFIG['art20']['minimum_student_approval_pct'] else 'NAO_ATENDE',{'elegiveis':len(eligible),'aprovados':ap,'rendimento_normativo':pct})
def calcular_art21(periodos_computaveis:Optional[int],periodos_regulares:Optional[int]):
    if periodos_computaveis is None or not periodos_regulares:return RuleResult('21','REQUER_CONFERENCIA',{},True)
    lim=periodos_regulares*float(MCN_CONFIG['art21']['max_regular_factor']); return RuleResult('21','ATENDE' if periodos_computaveis<=lim else 'NAO_ATENDE',{'periodos_computaveis':periodos_computaveis,'limite_150':lim})
