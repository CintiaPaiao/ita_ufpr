from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy import select

from src.config.settings import load_yaml, APP_CONFIG
from src.db.session import init_db, session_scope, database_ping, database_backend
from src.models.models import Cycle


DEFAULT_CYCLE_STATUS = "PREPARACAO_DADOS"
ALLOWED_CYCLE_STATUSES = {
    "PREPARACAO_DADOS",
    "ATIVO",
    "DADOS_VALIDADOS",
    "ENCERRADO",
}


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass
class BootstrapResult:
    database_ok: bool
    database_backend: str
    cycles_created: list[str]
    cycles_existing: list[str]
    default_cycle: str | None


def configured_default_cycles() -> list[dict]:
    """Retorna os ciclos institucionais declarados em ``configs/ciclos.yaml``.

    A configuração serve apenas como bootstrap inicial. Depois de cadastrados,
    os ciclos passam a ser administrados pelo banco/aplicação.
    """
    cfg = load_yaml("ciclos.yaml")
    return list(cfg.get("cycles", []) or [])


def ensure_default_cycles(session) -> tuple[list[str], list[str]]:
    """Garante, de forma idempotente, que os ciclos iniciais existam no banco.

    Não cria estudantes, avaliações ou dados sintéticos. Assim, a aplicação
    pode iniciar em produção com banco vazio e receber as bases reais pela UI.
    """
    created: list[str] = []
    existing: list[str] = []
    for item in configured_default_cycles():
        code = str(item.get("id") or item.get("codigo") or "").strip()
        if not code:
            continue
        current = session.scalar(select(Cycle).where(Cycle.codigo == code))
        if current:
            existing.append(code)
            continue
        status = str(item.get("status") or DEFAULT_CYCLE_STATUS).upper()
        if status not in ALLOWED_CYCLE_STATUSES:
            status = DEFAULT_CYCLE_STATUS
        session.add(Cycle(codigo=code, status=status))
        created.append(code)
    session.flush()
    return created, existing


def bootstrap_application() -> BootstrapResult:
    """Inicializa schema e ciclos básicos automaticamente no startup.

    Esta função substitui a dependência operacional de ``scripts/init_db.py``
    e ``scripts/load_sample_data.py`` para o deploy Streamlit.
    """
    init_db()
    if not database_ping():
        return BootstrapResult(False, database_backend(), [], [], None)
    with session_scope() as session:
        created, existing = ensure_default_cycles(session)
        cycles = list(session.scalars(select(Cycle).order_by(Cycle.codigo)))
    default_cycle = str(APP_CONFIG.get("app", {}).get("default_cycle") or "") or None
    if default_cycle and all(c.codigo != default_cycle for c in cycles):
        default_cycle = cycles[-1].codigo if cycles else None
    return BootstrapResult(True, database_backend(), created, existing, default_cycle)


def create_cycle(session, *, codigo: str, status: str = DEFAULT_CYCLE_STATUS) -> Cycle:
    codigo = codigo.strip()
    if not codigo:
        raise ValueError("Informe o código do ciclo.")
    if session.scalar(select(Cycle).where(Cycle.codigo == codigo)):
        raise ValueError(f"O ciclo {codigo} já existe.")
    status = status.upper()
    if status not in ALLOWED_CYCLE_STATUSES:
        raise ValueError(f"Status inválido: {status}")
    cycle = Cycle(codigo=codigo, status=status)
    session.add(cycle)
    session.flush()
    return cycle


def set_cycle_status(session, *, cycle_id: int, status: str) -> Cycle:
    status = status.upper()
    if status not in ALLOWED_CYCLE_STATUSES:
        raise ValueError(f"Status inválido: {status}")
    cycle = session.get(Cycle, cycle_id)
    if not cycle:
        raise ValueError("Ciclo não localizado.")
    cycle.status = status
    # Encerramento administrativo é diferente do congelamento técnico das bases.
    # O campo frozen_at é gerenciado exclusivamente pelo freeze_service.
    session.flush()
    return cycle


def activate_cycle(session, cycle_id: int) -> Cycle:
    return set_cycle_status(session, cycle_id=cycle_id, status="ATIVO")


def close_cycle(session, cycle_id: int) -> Cycle:
    return set_cycle_status(session, cycle_id=cycle_id, status="ENCERRADO")


def reopen_cycle(session, cycle_id: int) -> Cycle:
    cycle = session.get(Cycle, cycle_id)
    if not cycle:
        raise ValueError("Ciclo não localizado.")
    cycle.status = "ATIVO"
    # O encerramento administrativo não deve apagar o histórico de frozen_at.
    session.flush()
    return cycle
