import streamlit as st
from datetime import date
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,MNA
page_setup('MNA – Necessidade de Acompanhamento')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    c=cycles[-1];mod=st.selectbox('Modalidade',['ORIENTACAO','MONITORAMENTO','ACOMPANHAMENTO_PEDAGOGICO','ACOMPANHAMENTO_TECNICO_EDUCACIONAL','ACOMPANHAMENTO_MULTIPROFISSIONAL','PIAAP','ACAO_COLETIVA','ARTICULACAO_ACADEMICA']);inte=st.selectbox('Intensidade',['BAIXA','MEDIA','ALTA']);obj=st.text_area('Objetivo');resp=st.text_input('Responsável');prazo=st.date_input('Prazo',date.today());just=st.text_area('Justificativa')
    if st.button('Salvar'):s.add(MNA(student_id=stu.id,cycle_id=c.id,modalidade=mod,intensidade=inte,objetivo=obj,responsavel=resp,prazo=prazo,justificativa=just));st.success('MNA registrada.')
