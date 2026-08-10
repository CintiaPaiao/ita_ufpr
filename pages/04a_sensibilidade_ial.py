import streamlit as st
import pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import IALResult, Cycle
from src.services.sensitivity_service import analyze

page_setup("IAL – Análise de Sensibilidade", allowed_roles=("ADMIN","CHEFIA","AUDITOR"))
st.caption("Ferramenta de homologação. Não altera o IAL persistido nem substitui pactuação institucional.")
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not cycles:
        st.info("Nenhum ciclo cadastrado."); st.stop()
    opts={c.codigo:c for c in cycles}; code=st.selectbox("Ciclo",list(opts),index=len(opts)-1); cycle=opts[code]
    rows=list(s.scalars(select(IALResult).where(IALResult.cycle_id==cycle.id)))
records=[{"student_id":x.student_id,"r":x.r,"f":x.f,"p":x.p} for x in rows]
if not records:
    st.info("Sem IAL calculado para o ciclo."); st.stop()
result=analyze(records)
cols=st.columns(len(result))
for col,(name,data) in zip(cols,result.items()):
    col.subheader(name)
    col.dataframe(pd.DataFrame([{"faixa":k,"n":v} for k,v in data["bands"].items()]),hide_index=True,use_container_width=True)
base={x["student_id"]:x for x in result["40/35/25"]["records"]}
compare=[]
for scenario,data in result.items():
    if scenario=="40/35/25": continue
    moved=sum(1 for x in data["records"] if x["faixa"]!=base.get(x["student_id"],{}).get("faixa"))
    compare.append({"cenário":scenario,"mudanças_de_faixa":moved,"total":len(data["records"]),"percentual":round(100*moved/max(1,len(data["records"])),1)})
st.subheader("Migração em relação ao cenário 40/35/25")
st.dataframe(pd.DataFrame(compare),hide_index=True,use_container_width=True)
