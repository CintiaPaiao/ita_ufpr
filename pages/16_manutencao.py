import streamlit as st
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Maintenance
u=page_setup('Registro de Manutenção')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    mod=st.selectbox('Modalidade',['SEM_APOIO_ADICIONAL','COM_ORIENTACAO','COM_MONITORAMENTO','COM_ACOMPANHAMENTO','COM_PIAAP','COM_ARTICULACAO','COM_ACAO_COLETIVA']);marco=st.text_input('Próximo marco')
    if st.button('Registrar'):s.add(Maintenance(student_id=stu.id,cycle_id=cycles[-1].id,modalidade=mod,responsavel=u['username'],proximo_marco=marco));st.success('Manutenção registrada.')
