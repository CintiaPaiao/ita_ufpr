import streamlit as st, pandas as pd, datetime as dt
from src.core import *
from src.ui import setup,next_action
setup('Jornada do ciclo'); init_db(); cfg=load_config()
cycle=st.text_input('Ciclo','2025/2')
steps=['Preparar','Modelos','Importar','Validar','Congelar','Processar','Revisar','Selecionar','Distribuir','Analisar','Monitorar','Reavaliar']
st.progress(0.15,text='Etapas iniciais: modelos e importação')
st.write(' → '.join(steps))
up=st.file_uploader('Importar base Excel ou CSV',type=['xlsx','csv'])
if up:
    df=pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
    issues=validate_df(df); st.dataframe(df.head(20),use_container_width=True)
    if issues: st.error(f'{len(issues)} inconsistência(s)'); st.dataframe(pd.DataFrame(issues),use_container_width=True)
    else:
        st.success('Estrutura básica válida.');
        if st.button('Registrar importação validada'):
            raw=up.getvalue(); h=__import__('hashlib').sha256(raw).hexdigest(); con=connect();
            con.execute('INSERT INTO imports(cycle,filename,sha256,rows_n,grrs_n,status,created_at) VALUES(?,?,?,?,?,?,?)',(cycle,up.name,h,len(df),df.GRR.nunique(),'VALIDO',dt.datetime.now().isoformat()));con.commit();con.close();st.success('Importação registrada.')
st.divider(); responsible=st.text_input('Responsável pelo congelamento')
if st.button('Congelar ciclo',type='primary',disabled=not responsible):
    h=freeze_cycle(cycle,responsible); st.success(f'Ciclo congelado. Hash: {h[:16]}…')
next_action('Em preparação','Valide as bases e congele o ciclo antes do processamento oficial.')
