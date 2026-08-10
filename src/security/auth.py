import os,hashlib,hmac
def hash_password(p):return hashlib.sha256(p.encode()).hexdigest()
def authenticate(username,password):
    if os.getenv('APP_DEMO_MODE','true').lower()=='true':
        u=os.getenv('DEMO_USER','admin');h=os.getenv('DEMO_PASSWORD_HASH') or hash_password('admin')
        if hmac.compare_digest(username,u) and hmac.compare_digest(hash_password(password),h):return {'username':username,'display_name':'Administrador Demo','role':'ADMIN'}
def require_login():
    import streamlit as st
    if st.session_state.get('user'):return st.session_state['user']
    st.title('Acesso à aplicação PAE/UFPR');st.caption('Modo MVP. Em produção, substituir por autenticação institucional.')
    with st.form('login'):
        u=st.text_input('Usuário');p=st.text_input('Senha',type='password');ok=st.form_submit_button('Entrar')
    if ok:
        user=authenticate(u,p)
        if user:st.session_state['user']=user;st.rerun()
        st.error('Credenciais inválidas.')
    st.stop()
def require_role(*allowed):
    import streamlit as st
    user=require_login()
    if user['role'] not in allowed:st.error('Seu perfil não possui permissão.');st.stop()
    return user
