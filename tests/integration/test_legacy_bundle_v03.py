from io import BytesIO
import pandas as pd
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle,Student,LegacyAcademicSnapshot,Accompaniment,IALResult,MCNResult,Prioritization
from src.services.legacy_bundle_service import import_legacy_bundle
from src.services.processing_service import process_cycle


def _main_workbook():
    df=pd.DataFrame({
        "GRR":["GRR20260001","GRR20260002"],
        "NOME":["Pessoa A","Pessoa B"],
        "SETOR":["SETOR X","SETOR Y"],
        "curso":["Curso A","Curso B"],
        "renda-per-capta":[500,800],
        "ano-ingresso":[2024,2023],
        "TEMPO UFPR - SEM":[4,6],
        "ch-integralizada":[25.0,50.0],
        "qtd-matriculada":[5,4],
        "qtd-rep-frequencia":[3,1],
        "qtd-reprovacao-por-nota":[1,0],
        "qtd-matricula-cancelada":[0,1],
        "porcentagem-aprovacao":[20.0,50.0],
        "% Rep Freq 2024-2":[50.0,25.0],
        "% Rep Freq 2024-1":[25.0,0.0],
        "% Rep Freq 2023 -2":[0.0,25.0],
        "porcentagem-historica-de-reprovacao-frequencia":[0.25,0.1667],
        "apareceu-na-avaliacao-semestre-anterior?":[1,0],
        "ITA":[80,60],
    })
    b=BytesIO()
    with pd.ExcelWriter(b,engine="xlsxwriter") as w: df.to_excel(w,index=False,sheet_name="PLANILHA COMPLETA")
    return b.getvalue()


def _criteria_workbook():
    b=BytesIO()
    with pd.ExcelWriter(b,engine="xlsxwriter") as w:
        pd.DataFrame({"GRR":["GRR20260001"],"ATENDE AOS CRITÉRIOS?":["SIM"],"Observações":["registro de acompanhamento"],"Servidor de  Referência":["Prof A"]}).to_excel(w,index=False,sheet_name="Serviço Social")
        pd.DataFrame({"GRR":["GRR20260002"],"ATENDE AOS CRITÉRIOS?":["SIM"]}).to_excel(w,index=False,sheet_name="Pedagogia")
    return b.getvalue()


def test_legacy_bundle_and_processing(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'v03.db'}"); Base.metadata.create_all(eng); S=sessionmaker(bind=eng)
    with S() as s:
        s.add(Cycle(codigo="2026/1")); s.commit()
    with S() as s:
        out=import_legacy_bundle(s,main_filename="main.xlsx",main_raw=_main_workbook(),criteria_filename="criteria.xlsx",criteria_raw=_criteria_workbook(),cycle_code="2026/1",username="test")
        s.commit()
        assert out["main"]["imported"]==2
        assert out["criteria"]["imported"]==2
        assert len(list(s.scalars(select(LegacyAcademicSnapshot))))==2
        assert len(list(s.scalars(select(Accompaniment))))==2
    with S() as s:
        res=process_cycle(s,cycle_code="2026/1",username="test",n_cases=2,allow_incomplete=False); s.commit()
        assert res["legacy_mode"] is True
        assert res["universo"]==2
        assert len(list(s.scalars(select(IALResult))))==2
        assert len(list(s.scalars(select(MCNResult))))==10
        assert len(list(s.scalars(select(Prioritization))))==2
        first=s.scalar(select(Student).where(Student.grr=="GRR20260001"))
        art19=s.scalar(select(MCNResult).where(MCNResult.student_id==first.id,MCNResult.artigo=="19"))
        assert art19.status=="NAO_ATENDE"
        art20=s.scalar(select(MCNResult).where(MCNResult.student_id==first.id,MCNResult.artigo=="20"))
        assert art20.status=="REQUER_CONFERENCIA"
