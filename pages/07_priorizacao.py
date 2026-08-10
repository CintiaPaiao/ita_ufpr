import streamlit as st
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Prioritization,Student
from src.logging.audit import log_action
u=page_setup('Priorização e Seleção')
with session_scope() as s:
    rows=list(s.scalars(select(Prioritization).order_by(Prioritization.camada,Prioritization.ordem_na_camada)))
    for r in rows:
        stu=s.get(Student,r.student_id)
        with st.expander(f'{r.camada} • {stu.nome if stu else r.student_id} • {stu.grr if stu else ""}'):
            st.write(r.razoes);new=st.checkbox('Selecionado final',value=r.selecionado_final,key=f's{r.id}');reason=st.text_input('Justificativa se alterar',key=f'r{r.id}')
            if st.button('Salvar',key=f'b{r.id}'):
                if new!=r.selecionado_final and not reason.strip():st.error('Justificativa obrigatória.')
                else:
                    old=r.selecionado_final;r.selecionado_final=new;r.validado_equipe=True;r.alteracao_manual=(new!=old);r.justificativa_manual=reason or None
                    log_action(s,username=u['username'],action='ALTERAR_SELECAO',entity='priorizacao',entity_id=str(r.id),grr=stu.grr if stu else None,old_value=str(old),new_value=str(new),reason=reason);st.success('Registrado.')
