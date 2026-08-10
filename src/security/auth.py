from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
from sqlalchemy import select
from src.config.runtime import runtime_value, is_production, streamlit_users
from src.security.passwords import verify_password, hash_password

ROLES = {"ADMIN", "PROFISSIONAL", "CHEFIA", "COMISSAO", "AUDITOR"}


def _legacy_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _auth_from_secrets(username: str, password: str):
    for user in streamlit_users():
        if str(user.get("username", "")) != username:
            continue
        if str(user.get("role", "")).upper() not in ROLES:
            return None
        encoded = str(user.get("password_hash", ""))
        if verify_password(password, encoded):
            return {
                "username": username,
                "display_name": str(user.get("display_name") or username),
                "role": str(user.get("role")).upper(),
            }
    return None


def _auth_from_database(username: str, password: str):
    try:
        from src.db.session import session_scope
        from src.models.models import User
        with session_scope() as session:
            user = session.scalar(select(User).where(User.username == username, User.active == True))  # noqa: E712
            if user and verify_password(password, user.password_hash):
                return {"username": user.username, "display_name": user.display_name, "role": user.role}
    except Exception:
        return None
    return None


def authenticate(username: str, password: str):
    username = (username or "").strip()
    if not username or not password:
        return None
    user = _auth_from_secrets(username, password) or _auth_from_database(username, password)
    if user:
        return user
    demo_mode = str(runtime_value("APP_DEMO_MODE", "false" if is_production() else "true")).lower() == "true"
    if demo_mode and not is_production():
        demo_user = os.getenv("DEMO_USER", "admin")
        demo_hash = os.getenv("DEMO_PASSWORD_HASH") or _legacy_hash("admin")
        if hmac.compare_digest(username, demo_user) and hmac.compare_digest(_legacy_hash(password), demo_hash):
            return {"username": username, "display_name": "Administrador Demo", "role": "ADMIN"}
    return None


def _now():
    return datetime.now(timezone.utc)


def require_login():
    import streamlit as st
    timeout = int(runtime_value("SESSION_TIMEOUT_MINUTES", 120))
    max_attempts = int(runtime_value("MAX_LOGIN_ATTEMPTS", 5))
    user = st.session_state.get("user")
    expires = st.session_state.get("auth_expires_at")
    if user and expires and _now() < expires:
        st.session_state["auth_expires_at"] = _now() + timedelta(minutes=timeout)
        return user
    if user:
        st.session_state.pop("user", None)
        st.session_state.pop("auth_expires_at", None)
        st.warning("Sua sessão expirou. Entre novamente.")

    st.title("Acesso à aplicação PAE/UFPR")
    if is_production():
        st.caption("Ambiente de produção. Credenciais de demonstração estão desabilitadas.")
    else:
        st.caption("Ambiente de desenvolvimento/homologação.")
    attempts = int(st.session_state.get("login_attempts", 0))
    if attempts >= max_attempts:
        st.error("Número máximo de tentativas atingido nesta sessão. Recarregue a aplicação após revisar as credenciais.")
        st.stop()
    with st.form("login"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")
    if ok:
        authenticated = authenticate(username, password)
        if authenticated:
            st.session_state["user"] = authenticated
            st.session_state["auth_expires_at"] = _now() + timedelta(minutes=timeout)
            st.session_state["login_attempts"] = 0
            st.rerun()
        st.session_state["login_attempts"] = attempts + 1
        st.error("Credenciais inválidas.")
    st.stop()


def logout_button():
    import streamlit as st
    if st.sidebar.button("Sair", key="global_logout"):
        for key in ("user", "auth_expires_at", "login_attempts"):
            st.session_state.pop(key, None)
        st.rerun()


def require_role(*allowed):
    import streamlit as st
    user = require_login()
    allowed_set = {x.upper() for x in allowed}
    if user["role"].upper() not in allowed_set:
        st.error("Seu perfil não possui permissão para esta funcionalidade.")
        st.stop()
    return user


def bootstrap_user(session, *, username: str, display_name: str, role: str, password: str, overwrite: bool = False):
    from src.models.models import User
    role = role.upper()
    if role not in ROLES:
        raise ValueError("Perfil inválido")
    obj = session.scalar(select(User).where(User.username == username))
    if obj and not overwrite:
        return obj
    if not obj:
        obj = User(username=username, display_name=display_name, role=role, active=True)
        session.add(obj)
    obj.display_name = display_name
    obj.role = role
    obj.active = True
    obj.password_hash = hash_password(password)
    session.flush()
    return obj
