import streamlit as st
from sqlalchemy import select,func
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import *
page_setup('Visão Geral do Ciclo', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA', 'COMISSAO', 'AUDITOR'))
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not cycles:st.warning('Sem ciclos. Execute scripts/load_sample_data.py');st.stop()
    c={x.codigo:x for x in cycles}[st.selectbox('Ciclo',[x.codigo for x in cycles],index=len(cycles)-1)]
    models=[Student,IALResult,Prioritization,Allocation,Attendance,MAIC,MNA,PIAAP,Monitoring,Reassessment,CRPS,Appeal]
    names=['Universo','IAL','Priorizados','Distribuídos','Atendimentos','MAIC','MNA','PIAAP','Monitoramentos','Reavaliações','CRPS','Recursos']
    vals=[]
    for m in models:
        q=select(func.count()).select_from(m)
        if hasattr(m,'cycle_id'):q=q.where(m.cycle_id==c.id)
        vals.append(s.scalar(q) or 0)
cols=st.columns(4)
for i,(n,v) in enumerate(zip(names,vals)):cols[i%4].metric(n,v)
