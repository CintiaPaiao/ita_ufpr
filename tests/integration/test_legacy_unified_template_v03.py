from io import BytesIO
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle, Accompaniment, ProtectionFactor, LegacyProcessEvent
from src.services.legacy_bundle_service import import_legacy_bundle
from src.ingestion.legacy_ita_profile import profile_workbook_columns


def _workbook():
    df=pd.DataFrame({
        "GRR":["GRR20260001","GRR20260002"],
        "SETOR":["SETOR A","SETOR B"],
        "curso":["Curso A","Curso B"],
        "proafe":["REFUGIADO","TEA"],
        "renda-per-capta":[500,700],
        "classe":["A","B"],
        "nota":[20,10],
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
        "Serviço Social":["Serviço Social","Serviço Social"],
        "ATENDE AOS CRITÉRIOS?":["sim",None],
        "Observações":["registro social",None],
        "Servidor de  Referência":["Profissional A",None],
        "Serviço Pedagogia":["Pedagogia","Pedagogia"],
        "ATENDE AOS CRITÉRIOS? ":[None,"sim"],
        "Observações.2":[None,"registro pedagógico"],
        "Servidor de  Referência.2":[None,"Profissional B"],
        "responsavel 2025/1":["Profissional A",None],
        "1º parecer":["PERMANECE",None],
        "situação 1":["RECURSO",None],
        "respondeu o recurso final?":["SIM",None],
        "2º parecer":["PERMANECE",None],
    })
    b=BytesIO()
    with pd.ExcelWriter(b,engine="xlsxwriter") as w: df.to_excel(w,index=False,sheet_name="Sheet1")
    return b.getvalue(), df


def test_profile_and_embedded_blocks(tmp_path):
    raw,df=_workbook()
    profile=profile_workbook_columns(list(df.columns))
    assert profile["looks_like_ita_2025_unified"] is True
    assert profile["embedded_service_blocks"] >= 2
    eng=create_engine(f"sqlite:///{tmp_path/'legacy.db'}")
    Base.metadata.create_all(eng); S=sessionmaker(bind=eng)
    with S() as s:
        s.add(Cycle(codigo="2026/1")); s.commit()
    with S() as s:
        out=import_legacy_bundle(s,main_filename="unificada.xlsx",main_raw=raw,cycle_code="2026/1",username="test")
        s.commit()
        assert out["main"]["imported"]==2
        accomps=list(s.scalars(select(Accompaniment)))
        assert len(accomps)==2
        assert {a.setor for a in accomps}=={"SERVICO_SOCIAL_P4E","PEDAGOGIA_P4E"}
        factors={f.fator for f in s.scalars(select(ProtectionFactor))}
        assert "REFUGIO_MIGRACAO" in factors
        assert "DEFICIENCIA_ACESSIBILIDADE" in factors
        events=list(s.scalars(select(LegacyProcessEvent)))
        assert len(events)==1
        assert events[0].parecer_1=="PERMANECE"
