import streamlit as st
from src.core import load_config,save_config
from src.ui.helpers import setup
setup('Central de Configurações'); cfg=load_config()
st.warning('Alterações metodológicas devem ser pactuadas e versionadas. Parâmetros pendentes podem permanecer desabilitados por feature flag.')
with st.form('cfg'):
 st.subheader('Operação'); cfg['app']['selection_n']=st.number_input('N de estudantes selecionados',1,10000,int(cfg['app']['selection_n'])); cfg['app']['professionals']=st.number_input('Número de profissionais',1,100,int(cfg['app']['professionals']))
 st.subheader('IAL'); a=st.number_input('Peso rendimento',0.0,1.0,float(cfg['ial']['weights']['rendimento']),.05);b=st.number_input('Peso frequência',0.0,1.0,float(cfg['ial']['weights']['frequencia']),.05);c=st.number_input('Peso progressão',0.0,1.0,float(cfg['ial']['weights']['progressao']),.05); cov=st.number_input('Cobertura mínima calculável',0.0,1.0,float(cfg['ial']['coverage_partial_min']),.05)
 st.subheader('Normativos/fluxo'); cfg['mcn']['art20_min_approval']=st.number_input('Art. 20 — mínimo de aprovação (%)',0,100,int(cfg['mcn']['art20_min_approval']));cfg['mcn']['art21_multiplier']=st.number_input('Art. 21 — multiplicador do prazo',1.0,3.0,float(cfg['mcn']['art21_multiplier']),.1);cfg['workflow']['appeal_days']=st.number_input('Prazo de recurso (dias)',1,120,int(cfg['workflow']['appeal_days']))
 st.subheader('Feature flags')
 for k,v in cfg['features'].items(): cfg['features'][k]=st.toggle(k,value=bool(v))
 ok=st.form_submit_button('Salvar nova configuração',type='primary')
 if ok:
  if abs(a+b+c-1)>1e-6: st.error('Os pesos do IAL devem somar 1,00.')
  else:
   cfg['ial']['weights']={'rendimento':a,'frequencia':b,'progressao':c};cfg['ial']['coverage_partial_min']=cov;save_config(cfg);st.success('Configuração salva. Antes de uso oficial, congele uma nova versão do ciclo.')
st.subheader('Faixas do IAL'); st.dataframe(cfg['ial']['bands'],use_container_width=True)
