from sqlalchemy import func, select
from src.models.models import Student, Benefit, IALResult, Prioritization, Allocation, Attendance, MAIC, MNA, PIAAP, Monitoring, Reassessment, CRPS, Appeal

def cycle_metrics(session, cycle_id: int) -> dict:
    def c(model):
        stmt=select(func.count()).select_from(model)
        if hasattr(model,"cycle_id"):stmt=stmt.where(model.cycle_id==cycle_id)
        return session.scalar(stmt) or 0
    universo=session.scalar(select(func.count(func.distinct(Benefit.student_id))).where(Benefit.cycle_id==cycle_id)) or 0
    return {"universo":universo,"ial":c(IALResult),"selecionados":session.scalar(select(func.count()).select_from(Prioritization).where(Prioritization.cycle_id==cycle_id,Prioritization.selecionado_final==True)) or 0,"pre_priorizados":c(Prioritization),"distribuidos":c(Allocation),"atendimentos":c(Attendance),"maic":c(MAIC),"mna":c(MNA),"piaap":c(PIAAP),"monitoramentos":c(Monitoring),"reavaliacoes":c(Reassessment),"crps":c(CRPS),"recursos":c(Appeal)}
