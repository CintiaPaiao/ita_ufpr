import streamlit as st
from datetime import date
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Monitoring
from src.domain.monitoring.alerts import deadline_status
page_setup('Monitoramento')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    parte=st.selectbox('Parte',['ESTUDANTE','INSTITUICAO']);acao=st.text_area('Ação');resp=st.text_input('Responsável');prazo=st.date_input('Prazo',date.today());status=st.selectbox('Status',['PENDENTE','EXECUTADO','PARCIAL','NAO_EXECUTADO_COM_JUSTIFICATIVA']);just=st.text_area('Justificativa');pend=st.checkbox('Pendência institucional');st.info(deadline_status(prazo))
    if st.button('Registrar'):s.add(Monitoring(student_id=stu.id,cycle_id=cycles[-1].id,tipo_parte=parte,acao=acao,responsavel=resp,prazo=prazo,status=status,justificativa=just,pendencia_institucional=pend));st.success('Registrado.')
