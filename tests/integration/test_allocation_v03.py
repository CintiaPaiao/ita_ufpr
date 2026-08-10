from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from src.db.base import Base
from src.models.models import Cycle,Student,Prioritization,Allocation
from src.services.allocation_service import allocate_selected_cases

def test_allocation_after_final_validation(tmp_path):
    eng=create_engine(f"sqlite:///{tmp_path/'a.db'}"); Base.metadata.create_all(eng); S=sessionmaker(bind=eng)
    with S() as s:
        c=Cycle(codigo='2026/1'); s.add(c); s.flush()
        for i in range(10):
            st=Student(grr=f'GRR2026{i:04d}',nome=f'P{i}'); s.add(st); s.flush()
            s.add(Prioritization(student_id=st.id,cycle_id=c.id,camada='A',ordem_na_camada=i+1,razoes='teste',pre_selecionado=True,validado_equipe=True,selecionado_final=True))
        s.commit()
        out=allocate_selected_cases(s,cycle_code='2026/1',username='test'); s.commit()
        assert out['allocated']==10
        counts=list(out['counts'].values())
        assert max(counts)-min(counts)<=1
        assert len(list(s.scalars(select(Allocation))))==10
