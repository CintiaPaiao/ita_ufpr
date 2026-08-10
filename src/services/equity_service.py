from __future__ import annotations
from collections import defaultdict
from sqlalchemy import select
from src.models.models import Student, Prioritization, ProtectionFactor, IALResult


def equity_summary(session, cycle_id:int) -> dict:
    students={s.id:s for s in session.scalars(select(Student))}
    selected={p.student_id for p in session.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle_id,Prioritization.selecionado_final==True))}
    factors=list(session.scalars(select(ProtectionFactor).where(ProtectionFactor.cycle_id==cycle_id)))
    factor_students=defaultdict(set)
    for f in factors: factor_students[f.fator].add(f.student_id)
    by_campus=defaultdict(lambda:{"universo":0,"selecionados":0})
    by_course=defaultdict(lambda:{"universo":0,"selecionados":0})
    for sid,s in students.items():
        campus=s.campus or "NÃO INFORMADO"; course=s.curso or "NÃO INFORMADO"
        by_campus[campus]["universo"]+=1; by_course[course]["universo"]+=1
        if sid in selected:
            by_campus[campus]["selecionados"]+=1; by_course[course]["selecionados"]+=1
    by_factor=[]
    for factor,sids in sorted(factor_students.items()):
        by_factor.append({"fator":factor,"universo_com_fator":len(sids),"selecionados_com_fator":len(sids & selected)})
    return {"campus":dict(by_campus),"curso":dict(by_course),"fatores":by_factor,"selected_total":len(selected)}
