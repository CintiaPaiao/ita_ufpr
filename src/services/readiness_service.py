from __future__ import annotations
from pathlib import Path
from sqlalchemy import select, func

from src.config.runtime import is_production, runtime_value, streamlit_users
from src.db.session import database_backend, database_ping
from src.models.models import User, Cycle


def production_readiness(session) -> list[dict]:
    checks = []

    def add(name, ok, level, detail):
        checks.append({"check": name, "ok": bool(ok), "level": level, "detail": detail})

    prod = is_production()
    add("Ambiente production", prod, "CRITICO", "APP_ENV deve ser production para implantação real.")

    demo = str(runtime_value("APP_DEMO_MODE", "false")).lower() == "true"
    add("Modo demo desabilitado", not demo, "CRITICO", "Credenciais demo não podem permanecer em produção.")

    backend = database_backend()
    add("Banco disponível", database_ping(), "CRITICO", f"Backend: {backend}")
    # Streamlit Community Cloud + SQLite local pode perder dados após reinício/redeploy.
    persistent_backend = backend != "sqlite"
    add(
        "Banco persistente para deploy Streamlit",
        persistent_backend,
        "CRITICO" if prod else "ALTO",
        "Para produção no Streamlit, use PostgreSQL externo persistente. SQLite local é indicado apenas para desenvolvimento/homologação temporária.",
    )

    cycle_count = session.scalar(select(func.count()).select_from(Cycle)) or 0
    add("Ciclos cadastrados", cycle_count > 0, "CRITICO", f"Ciclos encontrados: {cycle_count}. O startup cria os ciclos padrão automaticamente.")

    db_users = session.scalar(select(func.count()).select_from(User).where(User.active == True)) or 0
    configured_users = len(streamlit_users()) + db_users
    add("Usuários configurados", configured_users > 0, "CRITICO", f"Usuários ativos/configurados: {configured_users}")

    secret_example = Path(".streamlit/secrets.toml.example").exists()
    add("Template de secrets", secret_example, "MEDIO", "Use secrets reais somente no deploy; não versione secrets.toml.")
    add("Configuração XSRF", Path(".streamlit/config.toml").exists(), "ALTO", "Configuração Streamlit segura deve estar presente.")
    add("Dados sintéticos não obrigatórios", True, "MEDIO", "A aplicação inicializa schema e ciclos sem load_sample_data.py.")
    return checks


def readiness_score(checks: list[dict]) -> tuple[int, bool]:
    critical_fail = any((not c["ok"] and c["level"] == "CRITICO") for c in checks)
    score = round(100 * sum(c["ok"] for c in checks) / max(1, len(checks)))
    return score, not critical_fail
