import streamlit as st,pandas as pd
from src.core import connect,init_db
from src.ui import setup
setup('Qualidade, auditoria e observabilidade');init_db();con=connect()
imports=pd.DataFrame([dict(r) for r in con.execute('SELECT * FROM imports ORDER BY created_at DESC').fetchall()]);freezes=pd.DataFrame([dict(r) for r in con.execute('SELECT cycle,hash_bases,app_version,responsible,frozen_at FROM cycle_freeze').fetchall()]);logs=pd.DataFrame([dict(r) for r in con.execute('SELECT * FROM audit ORDER BY created_at DESC LIMIT 200').fetchall()]);con.close()
st.subheader('Importações');st.dataframe(imports,use_container_width=True)
st.subheader('Ciclos congelados');st.dataframe(freezes,use_container_width=True)
st.subheader('Auditoria');st.dataframe(logs,use_container_width=True)
st.info('Auditoria de equidade deve usar dados agregados/minimizados e nunca alterar o IAL ou a CRPS.')
