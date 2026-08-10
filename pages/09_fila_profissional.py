import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Allocation, Student, Prioritization, Cycle
from src.services.case_service import build_case_summary

page_setup("Minha Fila de Casos", allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
prof=st.text_input("ID profissional", value="P1")
with session_scope() as s:
    rows=list(s.scalars(select(Allocation).where(Allocation.profissional_id==prof)))
    data=[]
    for a in rows:
        stu=s.get(Student,a.student_id); cy=s.get(Cycle,a.cycle_id); pr=s.scalar(select(Prioritization).where(Prioritization.student_id==a.student_id,Prioritization.cycle_id==a.cycle_id))
        summary=build_case_summary(s,a.student_id,a.cycle_id)
        data.append({"Ciclo":cy.codigo if cy else "","GRR":stu.grr if stu else "","Nome":stu.nome if stu else "","Camada":pr.camada if pr else "","IAL":round(summary['ial'].score,2) if summary['ial'] and summary['ial'].score is not None else None,"Fase":"REAVALIACAO" if summary['is_reassessment'] else "PRIMEIRA_ANALISE","Próxima ação":summary['next_action']})
st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
