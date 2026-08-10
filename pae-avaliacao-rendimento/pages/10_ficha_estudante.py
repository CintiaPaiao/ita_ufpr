import streamlit as st,pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import *
page_setup('Ficha Individual do Estudante')
with session_scope() as s:
    stu=select_student(s)
    if not stu:st.stop()
    st.subheader(f'{stu.nome} — {stu.grr}')
    tabs=st.tabs(['Resumo','Trajetória','MCN','IAL','Proteção','Acompanhamentos','Histórico','Contextualização','Atendimentos','MAIC','MNA','PIAAP','Manutenção','Monitoramento','Reavaliação','CRPS','Recursos','Timeline'])
    models=[None,AcademicHistory,MCNResult,IALResult,ProtectionFactor,Accompaniment,EvaluationHistory,Contextualization,Attendance,MAIC,MNA,PIAAP,Maintenance,Monitoring,Reassessment,CRPS,Appeal,None]
    for tab,model in zip(tabs,models):
        with tab:
            if model is None:
                if tab==tabs[0]:st.write({'GRR':stu.grr,'Curso':stu.curso,'Campus':stu.campus,'Currículo':stu.curriculo})
                else:st.info('Linha do tempo composta pelos registros das demais etapas.')
            else:
                rows=list(s.scalars(select(model).where(model.student_id==stu.id)));st.dataframe(pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows]),use_container_width=True,hide_index=True)
