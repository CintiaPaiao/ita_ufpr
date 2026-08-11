import streamlit as st,pandas as pd,plotly.express as px
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import IALResult
page_setup('IAL – Indicador Acadêmico Longitudinal', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA', 'AUDITOR'))
with session_scope() as s:rows=list(s.scalars(select(IALResult)))
df=pd.DataFrame([{c.name:getattr(r,c.name) for c in r.__table__.columns} for r in rows]);st.dataframe(df,width="stretch")
if not df.empty and df['score'].notna().any():st.plotly_chart(px.histogram(df,x='score',nbins=20,title='Distribuição do IAL'),width="stretch")
st.caption('IAL organiza prioridade acadêmica; não é indicador autônomo de suspensão.')
