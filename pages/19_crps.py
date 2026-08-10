import streamlit as st,json
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,CRPS
from src.domain.crps.checks import crps_readiness
u=page_setup('CRPS', allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    st.warning('CRPS é categórica e profissional; não é calculada pelo IAL.')
    checks={k:st.checkbox(l,key=k) for k,l in [('mcn_validated','MCN validada'),('maic_completed','MAIC concluída'),('hearing_completed','Escuta realizada'),('supports_checked','Apoios verificados'),('institutional_responsibility_checked','Responsabilidade institucional analisada'),('justifications_checked','Justificativas analisadas'),('cycle_comparison_completed','Comparação de ciclos concluída')]};re=st.checkbox('Caso em reavaliação');ok,miss=crps_readiness(checks,re);st.success('Requisitos disponíveis.') if ok else st.error('Pendências: '+', '.join(miss));cat=st.selectbox('Classificação profissional',['','CRPS-0','CRPS-1','CRPS-2','CRPS-3'],disabled=not ok);just=st.text_area('Justificativa',disabled=not ok)
    if st.button('Salvar',disabled=not ok or not cat):s.add(CRPS(student_id=stu.id,cycle_id=cycles[-1].id,categoria=cat,checklist_json=json.dumps(checks),profissional_id=u['username'],justificativa=just));st.success('CRPS registrada; nenhuma suspensão automática foi executada.')
