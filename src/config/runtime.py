from __future__ import annotations
import os
from typing import Any


def _streamlit_secret(path: tuple[str, ...]):
    try:
        import streamlit as st  # type: ignore
        value: Any = st.secrets
        for key in path:
            value = value[key]
        return value
    except Exception:
        return None


def runtime_value(key: str, default=None):
    """Resolve configuração em ordem: variável de ambiente -> Streamlit secrets -> default."""
    if key in os.environ:
        return os.environ[key]
    aliases = {
        "DATABASE_URL": [("database", "url"), ("DATABASE_URL",)],
        "APP_ENV": [("app", "env"), ("APP_ENV",)],
        "APP_DEMO_MODE": [("app", "demo_mode"), ("APP_DEMO_MODE",)],
        "SESSION_TIMEOUT_MINUTES": [("auth", "session_timeout_minutes"), ("SESSION_TIMEOUT_MINUTES",)],
        "MAX_LOGIN_ATTEMPTS": [("auth", "max_login_attempts"), ("MAX_LOGIN_ATTEMPTS",)],
    }
    for path in aliases.get(key, [(key,)]):
        value = _streamlit_secret(path)
        if value is not None:
            return value
    return default


def app_env() -> str:
    return str(runtime_value("APP_ENV", "development")).lower()


def is_production() -> bool:
    return app_env() == "production"


def streamlit_users() -> list[dict]:
    """Usuários definidos em `.streamlit/secrets.toml` no bloco [[auth.users]]."""
    try:
        import streamlit as st  # type: ignore
        users = st.secrets.get("auth", {}).get("users", [])
        return [dict(u) for u in users]
    except Exception:
        return []
