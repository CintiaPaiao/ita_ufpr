from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
import src.models.models  # noqa: F401
from src.models.models import Cycle
from src.services.bootstrap_service import create_cycle, activate_cycle, close_cycle, reopen_cycle


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_create_activate_close_reopen_cycle():
    s = make_session()
    c = create_cycle(s, codigo="2026/2")
    s.commit()
    assert c.status == "PREPARACAO_DADOS"
    activate_cycle(s, c.id); s.commit()
    assert s.get(Cycle, c.id).status == "ATIVO"
    close_cycle(s, c.id); s.commit()
    assert s.get(Cycle, c.id).status == "ENCERRADO"
    # Encerrar administrativamente não congela tecnicamente as bases.
    assert s.get(Cycle, c.id).frozen_at is None
    reopen_cycle(s, c.id); s.commit()
    assert s.get(Cycle, c.id).status == "ATIVO"
    s.close()


def test_duplicate_cycle_is_rejected():
    s = make_session()
    create_cycle(s, codigo="2026/2"); s.commit()
    try:
        create_cycle(s, codigo="2026/2")
        raised = False
    except ValueError:
        raised = True
    assert raised
    s.close()
