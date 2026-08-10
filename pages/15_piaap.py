import streamlit as st
from datetime import date
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,PIAAP,PIAAPAction
page_setup('PIAAP')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    c=cycles[-1];obj=st.text_area('Objetivo geral')
    if st.button('Criar PIAAP'):
        p=PIAAP(student_id=stu.id,cycle_id=c.id,objetivo_geral=obj,status='ATIVO');s.add(p);s.flush();st.session_state['pid']=p.id;st.success(f'PIAAP {p.id} criado.')
    pid=st.number_input('PIAAP ID',min_value=0,value=int(st.session_state.get('pid',0)))
    if pid:
        parte=st.selectbox('Parte responsável',['ESTUDANTE','INSTITUICAO']);desc=st.text_area('Ação');resp=st.text_input('Responsável');prazo=st.date_input('Prazo',date.today());ind=st.text_input('Indicador')
        if st.button('Adicionar ação'):s.add(PIAAPAction(piaap_id=int(pid),tipo='ACAO',descricao=desc,parte_responsavel=parte,responsavel=resp,prazo=prazo,indicador=ind,status='PENDENTE'));st.success('Ação adicionada.')
