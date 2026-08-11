import streamlit as st

from src.security.auth import require_login, logout_button
from src.db.session import database_backend, database_ping
from src.config.runtime import app_env, is_production
from src.services.bootstrap_service import bootstrap_application
from src.ui.ux import inject_app_css, info_card

st.set_page_config(page_title="PAE/UFPR – Avaliação de Rendimento", page_icon="🎓", layout="wide")

# Bootstrap idempotente: cria schema e ciclos institucionais, sem dados fictícios.
try:
    bootstrap = bootstrap_application()
except Exception as exc:
    st.error("Não foi possível inicializar a base de dados da aplicação.")
    if not is_production():
        st.exception(exc)
    else:
        st.info("Verifique DATABASE_URL / Streamlit Secrets e reinicie o aplicativo.")
    st.stop()

if not bootstrap.database_ok:
    st.error("O banco de dados não respondeu ao teste de conexão.")
    st.stop()

inject_app_css()
user = require_login()
logout_button()

st.title("Avaliação de Rendimento e Acompanhamento das Trajetórias Estudantis – PAE/UFPR")
st.caption("Versão 0.4.5.2 • jornada preservada da v0.4.4 + melhorias de usabilidade/configuração")
st.markdown(
    """
Aplicação institucional para apoiar a jornada semestral de Avaliação de Rendimento do PAE/UFPR.

**MCN, IAL, fatores de proteção, acompanhamento, MAIC, MNA, PIAAP, CRPS e decisão administrativa são dimensões distintas.**
A aplicação não executa suspensão automática e não converte vulnerabilidade, acompanhamento ou avaliação anterior em score punitivo.
"""
)
col1, col2, col3 = st.columns(3)
col1.metric("Ambiente", app_env())
col2.metric("Banco", database_backend())
col3.metric("Banco disponível", "SIM" if database_ping() else "NÃO")

if bootstrap.cycles_created:
    st.success("Ciclos iniciais criados automaticamente: " + ", ".join(bootstrap.cycles_created))

if is_production() and database_backend() == "sqlite":
    st.error(
        "Produção no Streamlit com SQLite local não garante persistência após reinícios/redeploys. "
        "Para dados reais, configure PostgreSQL externo persistente em DATABASE_URL / Streamlit Secrets."
    )
else:
    st.success("Backend de persistência compatível com o modo atual de execução.")

info_card("Por onde começar?", "Abra <b>Jornada do Ciclo</b> para visualizar a etapa atual. Para importar dados, use <b>Bases, Importação e Processamento</b>, que preserva integralmente o fluxo validado na v0.4.4.", icon="🧭")
st.info("O banco e os ciclos básicos são inicializados automaticamente; não é necessário executar scripts de dados sintéticos em produção.")
st.write(f"Usuário autenticado: **{user['display_name']}** ({user['role']})")
