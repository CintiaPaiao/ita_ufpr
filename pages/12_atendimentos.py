import streamlit as st
from datetime import datetime
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Attendance
u=page_setup('Atendimento / Escuta Profissional')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    c=cycles[-1]
    with st.form('f'):
        dados=st.text_area('Dados validados');bar=st.text_area('Novas barreiras/fatores');sin=st.text_area('Síntese necessária');ori=st.text_area('Orientações');enc=st.text_area('Encaminhamentos');mna=st.checkbox('Indica MNA');pia=st.checkbox('Indica PIAAP');marco=st.text_input('Próximo marco');ok=st.form_submit_button('Salvar')
    if ok:s.add(Attendance(student_id=stu.id,cycle_id=c.id,profissional_id=u['username'],data_atendimento=datetime.utcnow(),dados_validados=dados,novas_barreiras=bar,sintese=sin,orientacoes=ori,encaminhamentos=enc,indica_mna=mna,indica_piaap=pia,proximo_marco=marco));st.success('Atendimento registrado.')
