from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
import src.models.models  # noqa
from src.exports.unified_excel import export_unified_workbook

def test_unified_export_still_works(tmp_path):
    engine=create_engine(f"sqlite:///{tmp_path/'x.db'}")
    Base.metadata.create_all(engine)
    S=sessionmaker(bind=engine)
    with S() as s:
        data=export_unified_workbook(s)
    assert data[:2]==b'PK'
