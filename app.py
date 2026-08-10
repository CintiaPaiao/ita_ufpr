import streamlit as st
from src.security.auth import require_login, logout_button
from src.db.session import init_db, database_backend, database_ping
from src.config.runtime import app_env, is_production

st.set_page_config(page_title="PAE/UFPR – Avaliação de Rendimento", page_icon="🎓", layout="wide")
init_db()
user = require_login()
logout_button()

st.title("Avaliação de Rendimento e Acompanhamento das Trajetórias Estudantis – PAE/UFPR")
st.markdown(
    """
Aplicação institucional para apoiar a jornada semestral de Avaliação de Rendimento do PAE/UFPR.

**MCN, IAL, fatores de proteção, acompanhamento, MAIC, MNA, PIAAP, CRPS e decisão administrativa são dimensões distintas.**
A aplicação não executa suspensão automática e não converte vulnerabilidade, acompanhamento ou avaliação anterior em score punitivo.
"""
)
col1,col2,col3=st.columns(3)
col1.metric("Ambiente", app_env())
col2.metric("Banco", database_backend())
col3.metric("Banco disponível", "SIM" if database_ping() else "NÃO")
if is_production() and database_backend()=="sqlite":
    st.warning("Produção com SQLite está habilitada, mas para persistência multiusuária em deploy Streamlit recomenda-se banco PostgreSQL externo persistente.")
st.info("Use o menu lateral para seguir a jornada do ciclo. Em produção, revise primeiro a página 'Produção e Prontidão'.")
st.write(f"Usuário autenticado: **{user['display_name']}** ({user['role']})")
