from __future__ import annotations
import json
from sqlalchemy import select
from src.models.models import *
from src.domain.reassessment.compare import compare_cycles,detect_quantitative_persistence


def _cycle_sort_key(code: str):
    import re
    m=re.search(r"(\d{4}).*?([12])",str(code or ""))
    return (int(m.group(1)),int(m.group(2))) if m else (0,0)


def previous_cycle_result(session, student_id:int, current_cycle:Cycle):
    rows=list(session.execute(select(IALResult,Cycle).join(Cycle,IALResult.cycle_id==Cycle.id).where(IALResult.student_id==student_id,Cycle.codigo!=current_cycle.codigo)).all())
    rows=[r for r in rows if _cycle_sort_key(r[1].codigo) < _cycle_sort_key(current_cycle.codigo)]
    rows=sorted(rows,key=lambda rc:_cycle_sort_key(rc[1].codigo),reverse=True)
    return rows[0] if rows else (None,None)


def _student_cycle_rows(session, model, sid, cid):
    return list(session.scalars(select(model).where(model.student_id==sid,model.cycle_id==cid).order_by(model.id)))


def _latest(session, model, sid, cid):
    return session.scalar(select(model).where(model.student_id==sid,model.cycle_id==cid).order_by(model.id.desc()))


def _snapshot_metrics(session, sid, cid):
    snap=session.scalar(select(LegacyAcademicSnapshot).where(LegacyAcademicSnapshot.student_id==sid,LegacyAcademicSnapshot.cycle_id==cid))
    if snap:
        return {"aprovacao":snap.aprovacao_pct,"rep_freq":snap.qtd_rep_freq}
    # Fallback para histórico detalhado do ciclo.
    cycle=session.get(Cycle,cid)
    rows=list(session.scalars(select(AcademicHistory).where(AcademicHistory.student_id==sid,AcademicHistory.periodo==cycle.codigo)))
    eligible=[x for x in rows if x.cancelado is not True]
    approval=(100*sum(x.aprovado is True for x in eligible)/len(eligible)) if eligible and any(x.aprovado is not None for x in eligible) else None
    rf=sum(x.rep_freq is True for x in eligible) if eligible else None
    return {"aprovacao":approval,"rep_freq":rf}


def build_reassessment(session, student_id:int, cycle_id:int) -> dict:
    current_cycle=session.get(Cycle,cycle_id)
    current_ial=session.scalar(select(IALResult).where(IALResult.student_id==student_id,IALResult.cycle_id==cycle_id))
    prior_ial,prior_cycle=previous_cycle_result(session,student_id,current_cycle)
    current_mcn=_student_cycle_rows(session,MCNResult,student_id,cycle_id)
    prior_mcn=_student_cycle_rows(session,MCNResult,student_id,prior_cycle.id) if prior_cycle else []
    current_metrics=_snapshot_metrics(session,student_id,cycle_id)
    prior_metrics=_snapshot_metrics(session,student_id,prior_cycle.id) if prior_cycle else {"aprovacao":None,"rep_freq":None}
    comparison=compare_cycles(
        {"ial":prior_ial.score if prior_ial else None,**prior_metrics},
        {"ial":current_ial.score if current_ial else None,**current_metrics})
    prev_bad={x.artigo for x in prior_mcn if x.status in {"NAO_ATENDE","REQUER_CONFERENCIA"}}
    curr_bad={x.artigo for x in current_mcn if x.status in {"NAO_ATENDE","REQUER_CONFERENCIA"}}
    persistence=detect_quantitative_persistence(prev_bad,curr_bad) if prior_cycle else False

    professional_history={}
    if prior_cycle:
        prior_piaap=_latest(session,PIAAP,student_id,prior_cycle.id)
        professional_history={
            "maic": _latest(session,MAIC,student_id,prior_cycle.id),
            "mna": _latest(session,MNA,student_id,prior_cycle.id),
            "piaap": prior_piaap,
            "piaap_actions": list(session.scalars(select(PIAAPAction).where(PIAAPAction.piaap_id==prior_piaap.id))) if prior_piaap else [],
            "maintenance": _latest(session,Maintenance,student_id,prior_cycle.id),
            "monitoring": _student_cycle_rows(session,Monitoring,student_id,prior_cycle.id),
            "protections": _student_cycle_rows(session,ProtectionFactor,student_id,prior_cycle.id),
            "accompaniments": _student_cycle_rows(session,Accompaniment,student_id,prior_cycle.id),
            "attendances": _student_cycle_rows(session,Attendance,student_id,prior_cycle.id),
        }
    current_context={
        "protections":_student_cycle_rows(session,ProtectionFactor,student_id,cycle_id),
        "accompaniments":_student_cycle_rows(session,Accompaniment,student_id,cycle_id),
        "contextualization":_latest(session,Contextualization,student_id,cycle_id),
        "attendance":_latest(session,Attendance,student_id,cycle_id),
    }
    return {"prior_cycle":prior_cycle,"current_cycle":current_cycle,"comparison":comparison,"persistence":persistence,
            "prior_mcn":prior_mcn,"current_mcn":current_mcn,"prior_ial":prior_ial,"current_ial":current_ial,
            "professional_history":professional_history,"current_context":current_context}


def save_reassessment(session, student_id:int, cycle_id:int, *, escuta_realizada:bool, fundamentada:str|None):
    data=build_reassessment(session,student_id,cycle_id)
    existing=session.scalar(select(Reassessment).where(Reassessment.student_id==student_id,Reassessment.cycle_id==cycle_id))
    obj=existing or Reassessment(student_id=student_id,cycle_id=cycle_id,ciclo_anterior=data["prior_cycle"].codigo if data["prior_cycle"] else "NAO_IDENTIFICADO")
    obj.comparacao_json=json.dumps(data["comparison"],ensure_ascii=False)
    obj.persistencia_quantitativa=data["persistence"]
    obj.escuta_realizada=escuta_realizada
    obj.persistencia_fundamentada=fundamentada or None
    if not existing: session.add(obj)
    session.flush(); return obj,data
