from __future__ import annotations
from sqlalchemy import select
from src.models.models import *


def _one(session, model, sid, cid):
    return session.scalar(select(model).where(model.student_id==sid,model.cycle_id==cid).order_by(model.id.desc()))


def build_case_summary(session, student_id:int, cycle_id:int) -> dict:
    st=session.get(Student,student_id); cy=session.get(Cycle,cycle_id)
    mcn=list(session.scalars(select(MCNResult).where(MCNResult.student_id==student_id,MCNResult.cycle_id==cycle_id).order_by(MCNResult.artigo)))
    ial=_one(session,IALResult,student_id,cycle_id)
    pr=_one(session,Prioritization,student_id,cycle_id)
    alloc=_one(session,Allocation,student_id,cycle_id)
    ctx=_one(session,Contextualization,student_id,cycle_id)
    att=_one(session,Attendance,student_id,cycle_id)
    maic=_one(session,MAIC,student_id,cycle_id)
    mna=_one(session,MNA,student_id,cycle_id)
    maint=_one(session,Maintenance,student_id,cycle_id)
    reass=_one(session,Reassessment,student_id,cycle_id)
    crps=_one(session,CRPS,student_id,cycle_id)
    appeal=_one(session,Appeal,student_id,cycle_id)
    mon=list(session.scalars(select(Monitoring).where(Monitoring.student_id==student_id,Monitoring.cycle_id==cycle_id)))
    protections=list(session.scalars(select(ProtectionFactor).where(ProtectionFactor.student_id==student_id,ProtectionFactor.cycle_id==cycle_id)))
    accomp=list(session.scalars(select(Accompaniment).where(Accompaniment.student_id==student_id,Accompaniment.cycle_id==cycle_id)))
    legacy_process=_one(session,LegacyProcessEvent,student_id,cycle_id)
    prior_eval=bool(session.scalar(select(EvaluationHistory.id).where(EvaluationHistory.student_id==student_id).limit(1)))
    prior_ial=list(session.scalars(select(IALResult).join(Cycle,IALResult.cycle_id==Cycle.id).where(IALResult.student_id==student_id,Cycle.codigo!=cy.codigo).order_by(Cycle.codigo.desc())))
    is_reassessment=prior_eval or bool(prior_ial)
    selected=bool(pr and pr.selecionado_final)

    if not selected:
        next_action="AGUARDAR/VALIDAR SELECAO"
    elif not alloc:
        next_action="DISTRIBUIR CASO"
    elif is_reassessment and not reass:
        next_action="GERAR COMPARACAO DE REAVALIACAO"
    elif is_reassessment and reass and not reass.escuta_realizada:
        next_action="REALIZAR ESCUTA DE REAVALIACAO"
    elif not ctx:
        next_action="SOLICITAR CONTEXTUALIZACAO" if not is_reassessment else "SOLICITAR ATUALIZACAO DE CONTEXTUALIZACAO"
    elif not att:
        next_action="REALIZAR ESCUTA" if not is_reassessment else "REALIZAR ESCUTA DE REAVALIACAO"
    elif not maic or not maic.concluida:
        next_action="CONCLUIR MAIC"
    elif not mna:
        next_action="DEFINIR MNA"
    elif crps and crps.categoria=="CRPS-3" and not appeal:
        next_action="PREPARAR CONTRADITORIO/RECURSO"
    elif not maint and not (crps and crps.categoria=="CRPS-3"):
        next_action="REGISTRAR MANUTENCAO/RESPOSTA"
    elif any(x.status in {"PENDENTE","PARCIAL"} for x in mon):
        next_action="MONITORAR ACOES"
    elif appeal and appeal.status not in {"DECIDIDO","ENCERRADO"}:
        next_action="ACOMPANHAR RECURSO"
    else:
        next_action="ENCERRAR CICLO / AGUARDAR NOVA AVALIACAO"
    return {
        "student":st,"cycle":cy,"mcn":mcn,"ial":ial,"prioritization":pr,"allocation":alloc,
        "contextualization":ctx,"attendance":att,"maic":maic,"mna":mna,"maintenance":maint,
        "monitoring":mon,"protections":protections,"accompaniments":accomp,"legacy_process":legacy_process,
        "reassessment":reass,"crps":crps,"appeal":appeal,"is_reassessment":is_reassessment,"next_action":next_action,
    }
