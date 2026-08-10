from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.config.runtime import runtime_value

DATABASE_URL = str(runtime_value("DATABASE_URL", "sqlite:///database/pae.db"))
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Em deploy Streamlit, uma página multipágina pode ser executada diretamente sem
# que app.py tenha sido executado antes. Portanto, o schema precisa ser garantido
# pela própria camada de persistência e não apenas pelo entrypoint principal.
if IS_SQLITE:
    db_path = make_url(DATABASE_URL).database
    if db_path and db_path != ":memory:":
        Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

engine_kwargs = {"future": True, "pool_pre_ping": True}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
else:
    engine_kwargs.update({"pool_size": 5, "max_overflow": 10, "pool_recycle": 1800})

engine = create_engine(DATABASE_URL, **engine_kwargs)
_SCHEMA_LOCK = RLock()
_SCHEMA_READY = False

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.execute("PRAGMA busy_timeout=30000")
        cur.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db():
    """Cria idempotentemente as tabelas ORM existentes na versão atual."""
    import src.models.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def ensure_schema(force: bool = False) -> None:
    """Garante o schema antes de abrir qualquer sessão.

    Necessário no Streamlit multipágina, onde páginas em ``pages/`` podem ser
    executadas diretamente. A função é idempotente e protegida por lock para
    evitar corrida entre primeiras sessões simultâneas.
    """
    global _SCHEMA_READY
    if _SCHEMA_READY and not force:
        return
    with _SCHEMA_LOCK:
        if _SCHEMA_READY and not force:
            return
        init_db()
        _SCHEMA_READY = True


def database_backend() -> str:
    return "sqlite" if IS_SQLITE else engine.url.get_backend_name()


def database_ping() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@contextmanager
def session_scope():
    # Defesa em profundidade: nenhuma consulta pode ocorrer antes da criação
    # das tabelas, mesmo se a página for aberta sem passar por app.py.
    ensure_schema()
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
