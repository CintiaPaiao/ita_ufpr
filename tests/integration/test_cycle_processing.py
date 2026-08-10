from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import *
from src.services.processing_service import process_cycle

def test_processing_creates_mcn_ial_priority(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'p.db'}");Base.metadata.create_all(eng);S=sessionmaker(bind=eng)
    with S() as s:
        c=Cycle(codigo="2026/1");s.add(c);s.flush();st=Student(grr="GRR20260001",nome="Teste",codigo_curso="PED",curriculo="2025");s.add(st);s.flush()
        s.add(Benefit(student_id=st.id,cycle_id=c.id,modalidade="PAE",status="ATIVO"))
        s.add(CurriculumParameter(codigo_curso="PED",curriculo="2025",duracao_regular_periodos=8,ch_total=3200,ch_minima_art18=300,grau_evidencia="A"))
        s.add(IntegrationTime(student_id=st.id,cycle_id=c.id,ch_total=3200,ch_integralizada=400,periodos_computaveis=3,periodos_regulares=8))
        for i in range(4):s.add(AcademicHistory(student_id=st.id,periodo="2026/1",disciplina_codigo=f"D{i}",ch=60,aprovado=(i==0),rep_freq=(i in [1,2]),cancelado=False))
        s.commit();res=process_cycle(s,cycle_code="2026/1",username="test",n_cases=1,allow_incomplete=True);s.commit()
        assert res["universo"]==1
        assert len(list(s.scalars(select(MCNResult))))==5
        assert s.scalar(select(IALResult)) is not None
        assert s.scalar(select(Prioritization)) is not None
