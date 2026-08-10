import streamlit as st
from datetime import datetime
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.security.auth import require_role
from src.db.session import session_scope
from src.models.models import Cycle,CommissionEvent
require_role('ADMIN','COMISSAO','CHEFIA');page_setup('Comissão Paritária')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    st.caption('Registrar somente informação minimizada e necessária.');ev=st.selectbox('Evento',['RECEBIMENTO','ESCLARECIMENTO','DELIBERACAO','DECISAO']);res=st.text_area('Resumo minimizado');dec=st.text_area('Decisão')
    if st.button('Registrar'):s.add(CommissionEvent(student_id=stu.id,cycle_id=cycles[-1].id,evento=ev,data_evento=datetime.utcnow(),resumo_minimizado=res,decisao=dec));st.success('Evento registrado.')
