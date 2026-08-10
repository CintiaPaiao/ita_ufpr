import streamlit as st,pandas as pd
from sqlalchemy import select
from src.security.auth import require_login
def page_setup(title):
    st.set_page_config(page_title=title,page_icon='🎓',layout='wide');u=require_login();st.title(title);st.caption(f"Usuário: {u['display_name']} • Perfil: {u['role']}");return u
def model_table(model,limit=500):
    from src.db.session import session_scope
    with session_scope() as s:rows=list(s.scalars(select(model).limit(limit)))
    st.dataframe(pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows]),use_container_width=True,hide_index=True)
def select_student(session):
    from src.models.models import Student
    rows=list(session.scalars(select(Student).order_by(Student.nome)));opts={f'{x.nome} — {x.grr}':x for x in rows}
    if not opts:st.info('Nenhum estudante carregado.');return None
    return opts[st.selectbox('Estudante',list(opts))]
