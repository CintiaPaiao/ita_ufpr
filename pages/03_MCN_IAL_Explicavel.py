import streamlit as st
from src.core import art19,art20,ial,band,load_config
from src.ui.helpers import setup,next_action
setup('MCN e IAL explicáveis');cfg=load_config()
st.subheader('Demonstração segura de cálculo')
n=st.number_input('Disciplinas matriculadas',0,20,5);rf=st.number_input('Reprovações por frequência',0,20,1);ap=st.number_input('Componentes elegíveis aprovados',0,20,3);el=st.number_input('Componentes elegíveis',0,20,5)
r=st.number_input('R — risco de rendimento [0–1]',0.0,1.0,.5,.05);f=st.number_input('F — risco de frequência [0–1]',0.0,1.0,.3,.05);p=st.number_input('P — risco de progressão [0–1]',0.0,1.0,.4,.05)
s,cov,status=ial(r,f,p,cfg)
c1,c2,c3=st.columns(3);c1.metric('Art. 19',art19(n,rf));c2.metric('Art. 20',art20(ap,el,cfg['mcn']['art20_min_approval']));c3.metric('IAL',s if s is not None else 'N/C')
with st.expander('Como o IAL foi calculado?',expanded=True): st.json({'fonte':'valores informados nesta demonstração','componentes':{'R':r,'F':f,'P':p},'pesos':cfg['ial']['weights'],'cobertura':cov,'status':status,'faixa':band(s,cfg),'versão':cfg['app']['version']})
next_action('Cálculo de apoio concluído','Contextualize os resultados; não use IAL como decisão ou suspensão.')
