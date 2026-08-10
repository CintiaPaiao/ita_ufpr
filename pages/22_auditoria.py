import streamlit as st,pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import AuditLog,IALResult
page_setup('Auditoria e Equidade', allowed_roles=('ADMIN', 'CHEFIA', 'AUDITOR'))
with session_scope() as s:logs=list(s.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(1000)));ials=list(s.scalars(select(IALResult)))
st.subheader('Logs');st.dataframe(pd.DataFrame([{c.name:getattr(x,c.name) for c in x.__table__.columns} for x in logs]),use_container_width=True)
st.subheader('Distribuição do IAL');st.dataframe(pd.DataFrame([{'score':x.score,'faixa':x.faixa,'cobertura':x.cobertura} for x in ials]),use_container_width=True);st.caption('Marcadores PNAES servem para auditoria de equidade, nunca para aumentar o IAL.')
