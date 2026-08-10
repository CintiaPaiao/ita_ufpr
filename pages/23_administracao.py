import streamlit as st
from src.security.auth import require_role
from src.ui.common import page_setup
from src.db.session import session_scope
from src.exports.unified_excel import export_unified_workbook
from src.config.settings import IAL_CONFIG,MCN_CONFIG,PRIORITY_CONFIG,FEATURE_FLAGS
require_role('ADMIN','CHEFIA');page_setup('Administração e Configuração');st.json({'IAL':IAL_CONFIG,'MCN':MCN_CONFIG,'PRIORIZACAO':PRIORITY_CONFIG,'FEATURE_FLAGS':FEATURE_FLAGS})
with session_scope() as s:data=export_unified_workbook(s)
st.download_button('Exportar Planilha Unificada (19 abas)',data=data,file_name='planilha_unificada_pae.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
