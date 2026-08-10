import streamlit as st,pandas as pd
from src.ui.common import page_setup
from src.validation.normalization import normalize_dataframe_grr
from src.validation.data_quality import data_quality_report
page_setup('Bases e Qualidade dos Dados')
f=st.file_uploader('Excel/CSV para validação exploratória',type=['xlsx','xls','csv'])
if f:
    df=pd.read_csv(f) if f.name.lower().endswith('.csv') else pd.read_excel(f);st.dataframe(df.head(100),use_container_width=True)
    if 'GRR' in df.columns:st.dataframe(data_quality_report(normalize_dataframe_grr(df)),use_container_width=True)
    else:st.warning('Base sem coluna GRR.')
else:st.info('Importação operacional deve seguir schema + registro de arquivo; esta tela é exploratória.')
