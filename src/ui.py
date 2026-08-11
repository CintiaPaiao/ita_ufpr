import streamlit as st

def setup(title):
    st.set_page_config(page_title=title,page_icon='🎓',layout='wide')
    st.markdown('''<style>
    .block-container{padding-top:1.5rem;max-width:1450px}.stMetric{background:#f7f8fa;border:1px solid #e5e7eb;padding:12px;border-radius:12px}
    div[data-testid="stAlert"]{border-radius:10px}.small{color:#5f6b7a;font-size:.9rem}
    </style>''',unsafe_allow_html=True)
    st.title(title)
    st.caption('PAE/UFPR • versão 0.4.5 • apoio técnico-operacional — não substitui análise profissional')

def next_action(status, action):
    st.info(f'**Situação:** {status}  |  **Próxima ação:** {action}')
