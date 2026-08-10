import streamlit as st
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Prioritization, Student, Cycle
from src.logging.audit import log_action

user=page_setup("Priorização e Seleção", allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
if not cycles: st.stop()
cycle=st.selectbox("Ciclo",cycles,format_func=lambda c:c.codigo,index=len(cycles)-1)
layer_filter=st.multiselect("Camadas",["A","B","C","D","E"],default=["A","B","C","D","E"])
st.caption("A lista automática é preliminar. A seleção final exige validação da equipe. Fatores de proteção aumentam prioridade de análise/suporte, nunca proximidade automática de suspensão.")

with session_scope() as s:
    rows=list(s.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle.id,Prioritization.camada.in_(layer_filter)).order_by(Prioritization.camada,Prioritization.ordem_na_camada)))

c1,c2=st.columns(2)
with c1:
    confirm_bulk=st.checkbox("Confirmo que a equipe apreciou a lista preliminar e autorizou validar todos os casos exibidos.")
    if st.button("VALIDAR TODOS OS CASOS EXIBIDOS",disabled=not confirm_bulk):
        with session_scope() as s:
            items=list(s.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle.id,Prioritization.camada.in_(layer_filter))))
            for r in items:
                old=r.selecionado_final; r.validado_equipe=True; r.selecionado_final=True
                log_action(s,username=user["username"],action="VALIDACAO_COLETIVA_SELECAO",entity="priorizacao",entity_id=r.id,cycle_code=cycle.codigo,old_value=old,new_value=True,reason="Validação coletiva explícita da lista exibida")
        st.success("Seleção final registrada para os casos exibidos.")
with c2:
    st.metric("Casos exibidos",len(rows))

with session_scope() as s:
    rows=list(s.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle.id,Prioritization.camada.in_(layer_filter)).order_by(Prioritization.camada,Prioritization.ordem_na_camada)))
    for r in rows[:1000]:
        student=s.get(Student,r.student_id)
        with st.expander(f"{r.camada} • {r.ordem_na_camada} • {student.nome if student else r.student_id} • {student.grr if student else ''}"):
            st.write(r.razoes)
            new=st.checkbox("Selecionado final",value=r.selecionado_final,key=f"sel_{r.id}")
            if new != r.selecionado_final:
                reason=st.text_input("Justificativa da inclusão/exclusão",key=f"reason_{r.id}")
                if st.button("Salvar alteração",key=f"save_{r.id}"):
                    if not reason.strip(): st.error("Justificativa obrigatória.")
                    else:
                        old=r.selecionado_final; r.selecionado_final=new; r.validado_equipe=True; r.alteracao_manual=True; r.justificativa_manual=reason
                        log_action(s,username=user["username"],action="ALTERAR_SELECAO",entity="priorizacao",entity_id=r.id,cycle_code=cycle.codigo,grr=student.grr if student else None,old_value=old,new_value=new,reason=reason)
                        s.commit(); st.success("Alteração registrada.")
