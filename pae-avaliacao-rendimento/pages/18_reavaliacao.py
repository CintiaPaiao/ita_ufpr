import streamlit as st,json
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Reassessment
from src.domain.reassessment.compare import compare_cycles
page_setup('Reavaliação')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or len(cycles)<2:st.info('Reavaliação exige ciclo anterior e nova seleção.');st.stop()
    old=st.number_input('IAL anterior',0.0,100.0,50.0);new=st.number_input('IAL atual',0.0,100.0,50.0);oa=st.number_input('Aprovação anterior',0.0,100.0,50.0);na=st.number_input('Aprovação atual',0.0,100.0,50.0);orf=st.number_input('Rep. frequência anterior',0,20,0);nrf=st.number_input('Rep. frequência atual',0,20,0)
    comp=compare_cycles({'ial':old,'aprovacao':oa,'rep_freq':orf},{'ial':new,'aprovacao':na,'rep_freq':nrf});st.json(comp);pq=st.checkbox('Persistência quantitativa');esc=st.checkbox('Nova escuta realizada');pf=st.text_area('Persistência fundamentada – análise profissional')
    if st.button('Salvar'):s.add(Reassessment(student_id=stu.id,cycle_id=cycles[-1].id,ciclo_anterior=cycles[-2].codigo,comparacao_json=json.dumps(comp,ensure_ascii=False),persistencia_quantitativa=pq,persistencia_fundamentada=pf or None,escuta_realizada=esc));st.success('Reavaliação registrada.')
