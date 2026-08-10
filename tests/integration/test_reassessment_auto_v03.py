from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle,Student,IALResult,LegacyAcademicSnapshot,MCNResult
from src.services.reassessment_service import build_reassessment,save_reassessment

def test_auto_reassessment_between_cycles(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'r.db'}"); Base.metadata.create_all(eng); S=sessionmaker(bind=eng)
    with S() as s:
        c1=Cycle(codigo='2025/2'); c2=Cycle(codigo='2026/1'); s.add_all([c1,c2]); s.flush()
        st=Student(grr='GRR20260001',nome='Pessoa'); s.add(st); s.flush()
        s.add_all([
            IALResult(student_id=st.id,cycle_id=c1.id,r=.6,f=.5,p=None,score=55,cobertura=75,status='IAL PARCIAL – REQUER CONFERÊNCIA',faixa='Prioridade acadêmica elevada',versao='T'),
            IALResult(student_id=st.id,cycle_id=c2.id,r=.8,f=.7,p=None,score=75,cobertura=75,status='IAL PARCIAL – REQUER CONFERÊNCIA',faixa='Prioridade acadêmica intensiva',versao='T'),
            LegacyAcademicSnapshot(student_id=st.id,cycle_id=c1.id,aprovacao_pct=45,qtd_rep_freq=2),
            LegacyAcademicSnapshot(student_id=st.id,cycle_id=c2.id,aprovacao_pct=20,qtd_rep_freq=4),
            MCNResult(student_id=st.id,cycle_id=c1.id,artigo='19',status='NAO_ATENDE',regra_versao='T'),
            MCNResult(student_id=st.id,cycle_id=c2.id,artigo='19',status='NAO_ATENDE',regra_versao='T'),
        ]); s.commit()
        data=build_reassessment(s,st.id,c2.id)
        assert data['prior_cycle'].codigo=='2025/2'
        assert data['comparison']['ial']['status']=='AGRAVOU'
        assert data['persistence'] is True
        obj,_=save_reassessment(s,st.id,c2.id,escuta_realizada=True,fundamentada='Análise profissional'); s.commit()
        assert obj.escuta_realizada is True
        assert obj.persistencia_fundamentada=='Análise profissional'
