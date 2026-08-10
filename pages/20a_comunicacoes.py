import streamlit as st
from datetime import date
from sqlalchemy import select
from src.ui.common import page_setup, select_student
from src.db.session import session_scope
from src.models.models import Cycle, Notification
from src.services.communication_service import TEMPLATES, render_template

user=page_setup("Comunicações – Rascunhos Assistidos", allowed_roles=("ADMIN","PROFISSIONAL","CHEFIA"))
st.warning("A aplicação apenas gera e registra rascunhos. Comunicações restritivas não são enviadas automaticamente.")
with session_scope() as s:
    student=select_student(s); cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not student or not cycles: st.stop()
    cycle=cycles[-1]
    kind=st.selectbox("Tipo de comunicação", list(TEMPLATES))
    prazo=st.text_input("Prazo/orientação", "conforme comunicação institucional")
    draft=render_template(kind,nome=student.nome,ciclo=cycle.codigo,prazo=prazo)
    edited=st.text_area("Rascunho",draft,height=320)
    if st.button("Registrar rascunho"):
        s.add(Notification(student_id=student.id,cycle_id=cycle.id,tipo=kind,prazo=date.today(),status="RASCUNHO"))
        st.success("Rascunho registrado no processo. O texto deve ser copiado/revisado pelo profissional antes do envio institucional.")
