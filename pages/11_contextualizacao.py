import streamlit as st,json
from datetime import datetime
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,Contextualization
page_setup('Contextualização', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    c=cycles[-1];tipo=st.selectbox('Tipo',['CONTEXTUALIZACAO_INICIAL','ATUALIZACAO_REAVALIACAO']);status=st.selectbox('Status',['PENDENTE','RESPONDIDO','PARCIAL','OUTRA_VIA','NAO_RESPONDIDO']);txt=st.text_area('Manifestação/atualização')
    if st.button('Registrar'):
        s.add(Contextualization(student_id=stu.id,cycle_id=c.id,tipo=tipo,status=status,resposta_json=json.dumps({'manifestacao':txt},ensure_ascii=False),data_resposta=datetime.utcnow() if status=='RESPONDIDO' else None));st.success('Registrado. Não resposta permanece apenas como status processual.')
