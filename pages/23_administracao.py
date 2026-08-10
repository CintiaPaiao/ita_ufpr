import streamlit as st
import pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.security.auth import require_role, bootstrap_user
from src.db.session import session_scope
from src.exports.unified_excel import export_unified_workbook
from src.config.settings import IAL_CONFIG, MCN_CONFIG, PRIORITY_CONFIG, FEATURE_FLAGS
from src.models.models import User

require_role('ADMIN','CHEFIA')
current=page_setup('Administração e Configuração', allowed_roles=('ADMIN','CHEFIA'))

t1,t2,t3=st.tabs(["Configurações","Usuários","Exportações"])
with t1:
    st.json({'IAL':IAL_CONFIG,'MCN':MCN_CONFIG,'PRIORIZACAO':PRIORITY_CONFIG,'FEATURE_FLAGS':FEATURE_FLAGS})
    st.caption("Alterações metodológicas devem ser feitas em configuração versionada e submetidas à validação institucional.")
with t2:
    st.subheader("Usuários do banco")
    with session_scope() as s:
        users=list(s.scalars(select(User).order_by(User.username)))
        data=[{"username":u.username,"nome":u.display_name,"perfil":u.role,"ativo":u.active} for u in users]
    st.dataframe(pd.DataFrame(data),hide_index=True,use_container_width=True)
    if current['role']=='ADMIN':
        st.subheader("Criar/atualizar usuário")
        with st.form("user_admin"):
            username=st.text_input("Usuário")
            display=st.text_input("Nome de exibição")
            role=st.selectbox("Perfil",["ADMIN","PROFISSIONAL","CHEFIA","COMISSAO","AUDITOR"])
            password=st.text_input("Senha",type="password")
            overwrite=st.checkbox("Atualizar se já existir")
            ok=st.form_submit_button("Salvar usuário")
        if ok:
            if len(password)<10:
                st.error("Use senha com pelo menos 10 caracteres.")
            else:
                with session_scope() as s:
                    bootstrap_user(s,username=username,display_name=display or username,role=role,password=password,overwrite=overwrite)
                st.success("Usuário salvo com hash PBKDF2; a senha não é armazenada em texto claro.")
with t3:
    with session_scope() as s:
        data=export_unified_workbook(s)
    st.download_button('Exportar Planilha Unificada (19 abas)',data=data,file_name='planilha_unificada_pae.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
