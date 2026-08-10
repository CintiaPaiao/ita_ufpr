from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
import src.models.models  # noqa: F401
from src.models.models import Cycle, Student
from src.services.bootstrap_service import ensure_default_cycles


def test_default_cycles_are_created_without_sample_students():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        created, existing = ensure_default_cycles(session)
        session.commit()
        codes = [c.codigo for c in session.scalars(select(Cycle).order_by(Cycle.codigo))]
        students = list(session.scalars(select(Student)))
    assert "2025/2" in codes
    assert "2026/1" in codes
    assert students == []
    assert created


def test_bootstrap_is_idempotent():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        first_created, _ = ensure_default_cycles(session)
        session.commit()
        second_created, existing = ensure_default_cycles(session)
        session.commit()
    assert first_created
    assert second_created == []
    assert set(existing) >= {"2025/2", "2026/1"}
