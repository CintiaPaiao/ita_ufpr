from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import random
from datetime import date
from sqlalchemy import select
from src.db.session import init_db,session_scope
from src.models.models import *
from src.domain.ial.calculator import rendimento_component,frequencia_component,progressao_component,calculate_ial
from src.domain.mcn.rules import calcular_art19
from src.domain.prioritization.engine import PriorityInput,prioritize
random.seed(42);init_db()
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not cycles:
        c1=Cycle(codigo='2025/2',status='DADOS_VALIDADOS',code_version='0.3.0',mcn_version='MCN_1.0',ial_version='IAL_TESTE_1');c2=Cycle(codigo='2026/1',status='PREPARACAO_DADOS',code_version='0.3.0',mcn_version='MCN_1.0',ial_version='IAL_TESTE_1');s.add_all([c1,c2]);s.flush()
    else:c1,c2=cycles[0],cycles[-1]
    sts=[]
    for i in range(1,31):
        grr=f'GRR2026{i:04d}';st=s.scalar(select(Student).where(Student.grr==grr))
        if not st:
            st=Student(grr=grr,nome=f'Estudante Fictício {i:02d}',curso=random.choice(['Pedagogia','Engenharia Civil','Química','Geografia']),codigo_curso=random.choice(['PED','EC','QUI','GEO']),curriculo='2025',campus=random.choice(['Curitiba','Palotina']),ingresso='2024/1');s.add(st);s.flush()
        sts.append(st)
        if not s.scalar(select(Benefit).where(Benefit.student_id==st.id,Benefit.cycle_id==c2.id)):s.add(Benefit(student_id=st.id,cycle_id=c2.id,modalidade='Auxílio Permanência'))
        n=random.randint(3,6);rf=random.randint(0,3);ap=random.choice([20,35,50,65,80]);prev=max(0,min(100,ap+random.choice([-20,-10,0,10,20])));r=rendimento_component(ap,prev);f=frequencia_component(n,rf,[0,.2,0]);p=progressao_component(random.randint(15,80),100,random.randint(2,7),8,random.uniform(.5,1));ial=calculate_ial(r,f,p)
        if not s.scalar(select(IALResult).where(IALResult.student_id==st.id,IALResult.cycle_id==c2.id)):
            s.add(IALResult(student_id=st.id,cycle_id=c2.id,r=r,f=f,p=p,score=ial.score,cobertura=ial.coverage,status=ial.status,faixa=ial.band,versao='IAL_TESTE_1'));s.flush()
        rr=calcular_art19(n,rf)
        if not s.scalar(select(MCNResult).where(MCNResult.student_id==st.id,MCNResult.cycle_id==c2.id,MCNResult.artigo=='19')):s.add(MCNResult(student_id=st.id,cycle_id=c2.id,artigo='19',status=rr.status,evidencia=str(rr.evidencia),fonte='SINTETICA',qualidade_dado='VALIDADO',regra_versao='MCN_1.0'))
        if i%3==0:s.add(ProtectionFactor(student_id=st.id,cycle_id=c2.id,fator='PARENTALIDADE_CUIDADO',fonte='SIGA',status='IDENTIFICADO',data_registro=date.today(),status_atualidade='ATUAL',pre_analise=True))
        if i%4==0:s.add(Accompaniment(student_id=st.id,cycle_id=c2.id,setor='PEDAGOGIA',estado='ATIVO',data_ultimo_registro=date.today(),fonte='SINTETICA'))
        if i%5==0:s.add(EvaluationHistory(student_id=st.id,ciclo_codigo='2025/2',participou=True,resultado='MANUTENCAO',fase='PRIMEIRA_ANALISE',ial_anterior=max(0,(ial.score or 50)-10)))
    inputs=[]
    for st in sts:
        ir=s.scalar(select(IALResult).where(IALResult.student_id==st.id,IALResult.cycle_id==c2.id));m=list(s.scalars(select(MCNResult).where(MCNResult.student_id==st.id,MCNResult.cycle_id==c2.id)));re=s.scalar(select(EvaluationHistory).where(EvaluationHistory.student_id==st.id)) is not None
        inputs.append(PriorityInput(grr=st.grr,mcn_noncompliance_count=sum(x.status=='NAO_ATENDE' for x in m),ial_score=ir.score,ial_band=ir.faixa,reassessment=re,protective_priority=(st.id%3==0),intervention_need=(st.id%7==0)))
    for idx,res in enumerate(prioritize(inputs,30),1):
        st=s.scalar(select(Student).where(Student.grr==res.grr))
        if not s.scalar(select(Prioritization).where(Prioritization.student_id==st.id,Prioritization.cycle_id==c2.id)):s.add(Prioritization(student_id=st.id,cycle_id=c2.id,camada=res.layer,ordem_na_camada=idx,razoes='; '.join(res.reasons),pre_selecionado=True,validado_equipe=True,selecionado_final=True));s.flush()
    sels=list(s.scalars(select(Prioritization).where(Prioritization.cycle_id==c2.id,Prioritization.selecionado_final==True)))
    for idx,p in enumerate(sels):
        if not s.scalar(select(Allocation).where(Allocation.student_id==p.student_id,Allocation.cycle_id==c2.id)):s.add(Allocation(student_id=p.student_id,cycle_id=c2.id,profissional_id=f'P{idx%5+1}',complexidade='MEDIA'))
print('Dados sintéticos carregados.')
