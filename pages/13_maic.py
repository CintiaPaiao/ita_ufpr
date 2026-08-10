import streamlit as st
from sqlalchemy import select
from src.ui.common import page_setup,select_student
from src.db.session import session_scope
from src.models.models import Cycle,MAIC
u=page_setup('MAIC – Matriz de Análise Individualizada e Contextualizada')
with session_scope() as s:
    stu=select_student(s);cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not stu or not cycles:st.stop()
    c=cycles[-1]
    with st.form('f'):
        d=st.text_area('Dados objetivos');a=st.text_area('Análise profissional');r=st.text_area('Responsabilidade institucional');co=st.text_area('Conclusão profissional');done=st.checkbox('Concluída');ok=st.form_submit_button('Salvar')
    if ok:s.add(MAIC(student_id=stu.id,cycle_id=c.id,profissional_id=u['username'],dados_objetivos=d,analise_profissional=a,responsabilidade_institucional=r,conclusao=co,concluida=done));st.success('MAIC registrada; conclusão não é automática.')
