from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
import src.models.models as m
def test_sqlite(tmp_path):
    e=create_engine(f"sqlite:///{tmp_path/'x.db'}");Base.metadata.create_all(e);S=sessionmaker(bind=e)
    with S() as s:s.add(m.Student(grr='GRR20260001',nome='Teste'));s.commit()
    with S() as s:assert s.scalar(select(m.Student).where(m.Student.grr=='GRR20260001')).nome=='Teste'
