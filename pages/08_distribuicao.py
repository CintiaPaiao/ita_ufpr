import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Cycle,Allocation,Student
from src.services.allocation_service import allocate_selected_cases

user=page_setup("Distribuição da Equipe", allowed_roles=('ADMIN', 'CHEFIA'))
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
if not cycles: st.stop()
cycle=st.selectbox("Ciclo",cycles,format_func=lambda c:c.codigo,index=len(cycles)-1)
st.caption("A distribuição só utiliza estudantes validados como seleção final. O algoritmo balanceia carga e dá peso operacional a reavaliação/PIAAP/fluxos restritivos; não altera a prioridade metodológica.")
if st.button("DISTRIBUIR CASOS VALIDADOS",type="primary"):
    try:
        with session_scope() as s: res=allocate_selected_cases(s,cycle_code=cycle.codigo,username=user["username"],replace=True)
        st.success(f"{res['allocated']} casos distribuídos.")
        st.json(res["counts"])
    except Exception as e: st.exception(e)
with session_scope() as s:
    rows=list(s.scalars(select(Allocation).where(Allocation.cycle_id==cycle.id).order_by(Allocation.profissional_id)))
    data=[]
    for a in rows:
        stu=s.get(Student,a.student_id)
        data.append({"Profissional":a.profissional_id,"GRR":stu.grr if stu else "","Nome":stu.nome if stu else "","Complexidade operacional":a.complexidade,"Motivo":a.motivo_balanceamento})
st.dataframe(pd.DataFrame(data),width="stretch",hide_index=True)
