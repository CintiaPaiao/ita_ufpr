import streamlit as st
from datetime import datetime,date
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Appeal
page_setup('Recursos', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    etapa=st.selectbox('Etapa',['PRIMEIRO_RECURSO','DILIGENCIA','REANALISE','DECISAO_TECNICA','RECURSO_FINAL']);status=st.selectbox('Status',['RECEBIDO','EM_ANALISE','DILIGENCIA','DECIDIDO','ENCAMINHADO_COMISSAO']);txt=st.text_area('Registro/manifestação');dec=st.text_area('Decisão técnica');prazo=st.date_input('Prazo',date.today())
    if st.button('Registrar'):s.add(Appeal(student_id=stu.id,cycle_id=cycles[-1].id,etapa=etapa,data_recebimento=datetime.utcnow(),status=status,texto=txt,decisao=dec,prazo=prazo));st.success('Evento recursal registrado.')
