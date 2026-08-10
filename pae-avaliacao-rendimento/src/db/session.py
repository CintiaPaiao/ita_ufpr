from __future__ import annotations
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from src.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/pae.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor(); cur.execute("PRAGMA foreign_keys=ON"); cur.execute("PRAGMA journal_mode=WAL"); cur.execute("PRAGMA busy_timeout=5000"); cur.close()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)

def init_db():
    import src.models.models  # noqa
    Base.metadata.create_all(bind=engine)

@contextmanager
def session_scope():
    s=SessionLocal()
    try:
        yield s; s.commit()
    except Exception:
        s.rollback(); raise
    finally:
        s.close()
