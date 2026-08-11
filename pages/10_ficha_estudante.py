import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup, select_student
from src.db.session import session_scope
from src.models.models import *
from src.services.case_service import build_case_summary

page_setup("Ficha Individual do Estudante", allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    student=select_student(s)
    if not student: st.stop()
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    cycle=st.selectbox("Ciclo",cycles,format_func=lambda c:c.codigo,index=len(cycles)-1 if cycles else 0)
    if not cycle: st.stop()
    summary=build_case_summary(s,student.id,cycle.id)
    st.subheader(f"{student.nome} — {student.grr}")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Fase","REAVALIAÇÃO" if summary['is_reassessment'] else "PRIMEIRA ANÁLISE")
    c2.metric("IAL",f"{summary['ial'].score:.1f}" if summary['ial'] and summary['ial'].score is not None else "Não calculável")
    c3.metric("Cobertura",f"{summary['ial'].cobertura:.0f}%" if summary['ial'] else "—")
    c4.metric("Camada",summary['prioritization'].camada if summary['prioritization'] else "—")
    st.info("Próxima ação: **"+summary['next_action']+"**")
    if summary['mcn']:
        st.write("MCN:"," • ".join(f"Art.{x.artigo}: {x.status}" for x in summary['mcn']))
    if summary['protections']:
        st.write("Proteção conhecida:",", ".join(sorted({x.fator for x in summary['protections']})))
    if summary['accompaniments']:
        st.write("Acompanhamentos:",", ".join(sorted({x.setor for x in summary['accompaniments']})))
    tabs=st.tabs(["Trajetória/Snapshot","MCN","IAL","Proteção","Acompanhamentos","Histórico","Contextualização","Atendimentos","MAIC","MNA","PIAAP","Manutenção","Monitoramento","Reavaliação","CRPS","Recursos","Timeline"])
    models=[LegacyAcademicSnapshot,MCNResult,IALResult,ProtectionFactor,Accompaniment,EvaluationHistory,Contextualization,Attendance,MAIC,MNA,PIAAP,Maintenance,Monitoring,Reassessment,CRPS,Appeal,None]
    for tab,model in zip(tabs,models):
        with tab:
            if model is None: st.info("A linha do tempo é composta pelos registros datados das etapas anteriores.")
            elif model is EvaluationHistory:
                rows=list(s.scalars(select(model).where(model.student_id==student.id)))
                st.dataframe(pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows]),width="stretch",hide_index=True)
            else:
                rows=list(s.scalars(select(model).where(model.student_id==student.id,model.cycle_id==cycle.id)))
                st.dataframe(pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows]),width="stretch",hide_index=True)
