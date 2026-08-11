import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup, select_student
from src.db.session import session_scope
from src.models.models import Cycle
from src.services.reassessment_service import build_reassessment,save_reassessment

page_setup("Reavaliação – comparação automática entre ciclos", allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    student=select_student(s); cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not student or not cycles: st.stop()
    cycle=st.selectbox("Ciclo atual",cycles,format_func=lambda c:c.codigo,index=len(cycles)-1)
    data=build_reassessment(s,student.id,cycle.id)
    if not data['prior_cycle']:
        st.info("Não há resultado anterior armazenado para comparação automática. A rota de reavaliação só se aplica quando existe avaliação anterior e nova seleção."); st.stop()
    st.subheader(f"Comparação {data['prior_cycle'].codigo} → {cycle.codigo}")
    c1,c2,c3=st.columns(3)
    for col,key,label in [(c1,'ial','IAL'),(c2,'aprovacao','Aprovação'),(c3,'rep_freq','Rep. frequência')]:
        item=data['comparison'][key]
        col.metric(label, item.get('atual') if item.get('atual') is not None else '—', delta=item.get('status'))
    st.write("**MCN anterior:**", " • ".join(f"Art.{x.artigo} {x.status}" for x in data['prior_mcn']) or "—")
    st.write("**MCN atual:**", " • ".join(f"Art.{x.artigo} {x.status}" for x in data['current_mcn']) or "—")
    st.write("**Persistência quantitativa detectada:**","SIM" if data['persistence'] else "NÃO")
    st.caption("Persistência quantitativa é apenas detecção de recorrência. Persistência fundamentada depende de registros, apoios, responsabilidade institucional e nova escuta.")

    ph=data['professional_history']
    st.subheader("Registro do ciclo anterior recuperado automaticamente")
    rows=[
        {"dimensão":"MAIC","registro":"SIM" if ph.get('maic') else "NÃO"},
        {"dimensão":"MNA","registro":ph.get('mna').modalidade if ph.get('mna') else "NÃO"},
        {"dimensão":"PIAAP","registro":"SIM" if ph.get('piaap') else "NÃO"},
        {"dimensão":"Ações PIAAP","registro":len(ph.get('piaap_actions',[]))},
        {"dimensão":"Monitoramentos","registro":len(ph.get('monitoring',[]))},
        {"dimensão":"Acompanhamentos","registro":len(ph.get('accompaniments',[]))},
        {"dimensão":"Atendimentos","registro":len(ph.get('attendances',[]))},
    ]
    st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
    if ph.get('monitoring'):
        st.write("**Monitoramento anterior:**")
        st.dataframe(pd.DataFrame([{"parte":x.tipo_parte,"ação":x.acao,"status":x.status,"pendência institucional":x.pendencia_institucional} for x in ph['monitoring']]),width="stretch",hide_index=True)

    st.subheader("Garantia de nova escuta")
    escuta=st.checkbox("Nova escuta de reavaliação realizada")
    fundamentada=st.text_area("Verificação fundamentada da persistência – análise profissional",
        help="Considere comparação longitudinal, ações pactuadas, ofertas institucionais, barreiras/fatores de proteção e a nova escuta. Não é preenchido automaticamente.")
    if st.button("SALVAR REAVALIAÇÃO"):
        obj,_=save_reassessment(s,student.id,cycle.id,escuta_realizada=escuta,fundamentada=fundamentada)
        st.success(f"Reavaliação #{obj.id} registrada.")
