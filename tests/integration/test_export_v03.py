from io import BytesIO
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle,Student,Benefit,LegacyAcademicSnapshot
from src.exports.unified_excel import export_unified_workbook

def test_export_has_19_expected_sheets_and_snapshot(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'e.db'}"); Base.metadata.create_all(eng); S=sessionmaker(bind=eng)
    with S() as s:
        c=Cycle(codigo='2026/1'); st=Student(grr='GRR20260001',nome='Pessoa'); s.add_all([c,st]); s.flush()
        s.add(Benefit(student_id=st.id,cycle_id=c.id,modalidade='PAE',status='ATIVO'))
        s.add(LegacyAcademicSnapshot(student_id=st.id,cycle_id=c.id,aprovacao_pct=40,qtd_matriculada=5,qtd_rep_freq=2)); s.commit()
        raw=export_unified_workbook(s)
    xl=pd.ExcelFile(BytesIO(raw))
    assert len(xl.sheet_names)==19
    assert xl.sheet_names[0]=='00_CONTROLE'
    assert '18_DICIONARIO_DADOS' in xl.sheet_names
    uni=pd.read_excel(BytesIO(raw),sheet_name='01_UNIVERSO')
    assert 'legado_aprovacao_pct' in uni.columns
    assert float(uni.loc[0,'legado_aprovacao_pct'])==40
