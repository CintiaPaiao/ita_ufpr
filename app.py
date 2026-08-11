import streamlit as st
from src.core import init_db,load_config,connect
from src.ui.helpers import setup,next_action
init_db(); cfg=load_config(); setup('Avaliação de Rendimento e Trajetórias Estudantis')
con=connect();
counts={t:con.execute(f'SELECT COUNT(*) c FROM {t}').fetchone()['c'] for t in ['students','imports','results','professional_records']}; con.close()
c1,c2,c3,c4=st.columns(4)
c1.metric('Estudantes',counts['students']);c2.metric('Bases importadas',counts['imports']);c3.metric('Resultados',counts['results']);c4.metric('Registros profissionais',counts['professional_records'])
next_action('Ambiente pronto','Abra “Jornada do ciclo” para preparar, validar e congelar o ciclo.')
st.subheader('Jornada orientada')
st.write('Preparar → Modelos → Importar → Validar → Congelar → Processar → Revisar → Selecionar → Distribuir → Analisar → Monitorar → Reavaliar')
st.warning('MCN ≠ IAL ≠ fatores de proteção ≠ acompanhamento ≠ MAIC ≠ MNA ≠ PIAAP ≠ CRPS ≠ decisão administrativa.')
st.subheader('Configuração ativa')
st.json({'versão':cfg['app']['version'],'N seleção':cfg['app']['selection_n'],'pesos IAL':cfg['ial']['weights'],'feature flags':cfg['features']})
