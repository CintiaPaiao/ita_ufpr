import streamlit as st
import pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Cycle
from src.services.equity_service import equity_summary

page_setup("Auditoria de Equidade", allowed_roles=("ADMIN","CHEFIA","AUDITOR"))
st.caption("Painel agregado para detectar efeitos desproporcionais. Marcadores protetivos não alteram IAL nem CRPS.")
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not cycles: st.stop()
    opts={c.codigo:c for c in cycles}; code=st.selectbox("Ciclo",list(opts),index=len(opts)-1)
    data=equity_summary(s,opts[code].id)
for title,key in [("Por campus","campus"),("Por curso","curso")]:
    st.subheader(title)
    rows=[]
    for name,v in data[key].items():
        rows.append({"grupo":name,**v,"taxa_selecao_pct":round(100*v["selecionados"]/max(1,v["universo"]),1)})
    st.dataframe(pd.DataFrame(rows).sort_values("taxa_selecao_pct",ascending=False),hide_index=True,use_container_width=True)
st.subheader("Fatores de proteção – distribuição agregada")
st.dataframe(pd.DataFrame(data["fatores"]),hide_index=True,use_container_width=True)
