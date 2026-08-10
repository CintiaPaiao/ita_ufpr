from __future__ import annotations
from sqlalchemy import select, delete
from src.models.models import Cycle, Prioritization, Allocation, EvaluationHistory, PIAAP, CRPS
from src.domain.allocation.engine import distribute_round_robin
from src.config.settings import load_yaml
from src.logging.audit import log_action


def allocate_selected_cases(session, *, cycle_code: str, username: str, replace: bool=True):
    cycle=session.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    if not cycle: raise ValueError("Ciclo não cadastrado")
    selected=list(session.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle.id,Prioritization.selecionado_final==True).order_by(Prioritization.camada,Prioritization.ordem_na_camada)))
    if not selected: raise ValueError("Nenhum caso foi validado como seleção final.")
    if replace:
        session.execute(delete(Allocation).where(Allocation.cycle_id==cycle.id))
    professionals=load_yaml("servidores.yaml").get("professionals",[])
    cases=[]
    for pr in selected:
        reass=bool(session.scalar(select(EvaluationHistory.id).where(EvaluationHistory.student_id==pr.student_id).limit(1)))
        piaap=bool(session.scalar(select(PIAAP.id).where(PIAAP.student_id==pr.student_id).limit(1)))
        crps=bool(session.scalar(select(CRPS.id).where(CRPS.student_id==pr.student_id).limit(1)))
        complexity_rank=3 if crps else (2 if piaap or reass else 1)
        cases.append({"student_id":pr.student_id,"cycle_id":cycle.id,"grr":str(pr.student_id),"reassessment":reass,"complexity_rank":complexity_rank})
    out=distribute_round_robin(cases,professionals)
    for x in out:
        session.add(Allocation(student_id=x["student_id"],cycle_id=cycle.id,profissional_id=x["professional_id"],complexidade={1:"PADRAO",2:"ELEVADA",3:"RESTRITIVA"}.get(x["complexity_rank"],"PADRAO"),motivo_balanceamento="Distribuição assistida v0.3: carga + reavaliação/PIAAP/CRPS."))
    cycle.status="DISTRIBUIDO"
    log_action(session,username=username,action="DISTRIBUIR_CASOS",entity="ciclo",entity_id=cycle.id,cycle_code=cycle_code,new_value={"casos":len(out),"profissionais":len(professionals)},reason="Distribuição assistida após validação da seleção final")
    session.flush()
    counts={p["id"]:sum(1 for x in out if x["professional_id"]==p["id"]) for p in professionals}
    return {"allocated":len(out),"counts":counts}
