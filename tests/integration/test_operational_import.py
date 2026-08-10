from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle,Student,Benefit,ImportedFile
from src.schemas.import_contracts import validate_import,canonicalize
from src.ingestion.persistence import import_canonical
import pandas as pd

def test_beneficiary_import_persists(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'x.db'}");Base.metadata.create_all(eng);S=sessionmaker(bind=eng)
    df=pd.DataFrame({"GRR":["20260001"],"NOME":["Pessoa Teste"],"CURSO":["Pedagogia"],"AUXILIOS":["Permanência"]})
    val=validate_import(df,"SIGA_BENEFICIARIOS");assert val.valid
    can=canonicalize(df,"SIGA_BENEFICIARIOS",val.mapping)
    with S() as s:
        c=Cycle(codigo="2026/1");s.add(c);s.flush();res=import_canonical(s,base_type="SIGA_BENEFICIARIOS",df=can,cycle=c);s.commit()
        assert res["imported"]==1
        assert s.scalar(select(Student)).grr=="GRR20260001"
        assert s.scalar(select(Benefit)) is not None
