import streamlit as st,pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Allocation,Student,Prioritization
page_setup('Minha Fila de Casos');prof=st.text_input('ID profissional',value='P1')
with session_scope() as s:
    data=[]
    for a in s.scalars(select(Allocation).where(Allocation.profissional_id==prof)):
        stu=s.get(Student,a.student_id);p=s.scalar(select(Prioritization).where(Prioritization.student_id==a.student_id,Prioritization.cycle_id==a.cycle_id));data.append({'GRR':stu.grr,'Nome':stu.nome,'Camada':p.camada if p else '', 'Complexidade':a.complexidade,'Próxima ação':'Abrir ficha'})
st.dataframe(pd.DataFrame(data),use_container_width=True)
