import streamlit as st
from src.security.auth import require_login
from src.db.session import init_db
st.set_page_config(page_title='PAE/UFPR – Avaliação de Rendimento',page_icon='🎓',layout='wide')
init_db();user=require_login()
st.title('Avaliação de Rendimento e Acompanhamento das Trajetórias Estudantis – PAE/UFPR')
st.markdown('**MCN, IAL, fatores de proteção, acompanhamento, MAIC, MNA e CRPS são dimensões distintas. A aplicação não decide suspensão automaticamente.**')
st.info('Use o menu lateral para navegar. Banco padrão do MVP: SQLite.')
st.write(f"Usuário autenticado: **{user['display_name']}** ({user['role']})")
