from __future__ import annotations
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.config.runtime import runtime_value

DATABASE_URL = str(runtime_value("DATABASE_URL", "sqlite:///database/pae.db"))
IS_SQLITE = DATABASE_URL.startswith("sqlite")
engine_kwargs = {"future": True, "pool_pre_ping": True}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
else:
    engine_kwargs.update({"pool_size": 5, "max_overflow": 10, "pool_recycle": 1800})

engine = create_engine(DATABASE_URL, **engine_kwargs)

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
    import src.models.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


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
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
