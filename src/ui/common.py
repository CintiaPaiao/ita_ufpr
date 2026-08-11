from __future__ import annotations
import streamlit as st
import pandas as pd
from sqlalchemy import select
from src.security.auth import require_login, require_role, logout_button
from src.config.runtime import app_env, is_production
from src.services.bootstrap_service import bootstrap_application
from src.ui.ux import inject_app_css


def page_setup(title: str, allowed_roles: tuple[str, ...] | None = None):
    st.set_page_config(page_title=title, page_icon="🎓", layout="wide")
    # Streamlit multipágina pode executar esta página sem executar app.py.
    # Bootstrap aqui garante schema + ciclos em qualquer rota de entrada.
    try:
        bootstrap = bootstrap_application()
        if not bootstrap.database_ok:
            st.error("O banco de dados não respondeu ao teste de conexão.")
            st.stop()
    except Exception as exc:
        st.error("Não foi possível inicializar a base de dados da aplicação.")
        if not is_production():
            st.exception(exc)
        else:
            st.info("Verifique DATABASE_URL / Streamlit Secrets e reinicie o aplicativo.")
        st.stop()
    inject_app_css()
    user = require_role(*allowed_roles) if allowed_roles else require_login()
    st.title(title)
    st.caption(f"Usuário: {user['display_name']} • Perfil: {user['role']} • Ambiente: {app_env()}")
    logout_button()
    if not is_production():
        st.sidebar.info("Ambiente de desenvolvimento/homologação")
    return user


def safe_exception(exc: Exception, *, prefix: str = "Não foi possível concluir a operação."):
    """Evita expor stack traces e detalhes sensíveis em produção."""
    if is_production():
        st.error(prefix)
    else:
        st.exception(exc)


def model_table(model, title=None, limit=500):
    from src.db.session import session_scope
    if title:
        st.subheader(title)
    with session_scope() as session:
        rows = list(session.scalars(select(model).limit(limit)))
        data = [{c.name: getattr(r, c.name) for c in model.__table__.columns} for r in rows]
    st.dataframe(pd.DataFrame(data), width="stretch", hide_index=True)


def select_student(session):
    from src.models.models import Student
    students = list(session.scalars(select(Student).order_by(Student.nome)))
    options = {f"{x.nome} — {x.grr}": x for x in students}
    if not options:
        st.info("Nenhum estudante carregado.")
        return None
    key = st.selectbox("Estudante", list(options))
    return options[key]


def mask_grr(grr: str | None) -> str:
    if not grr:
        return ""
    return grr[:5] + "***" + grr[-2:]
