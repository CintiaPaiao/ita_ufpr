import streamlit as st
from src.core import crps3_allowed,load_config
from src.ui import setup,next_action
setup('CRPS, garantias e recursos');cfg=load_config()
if not cfg['features']['crps']: st.warning('CRPS desabilitada por feature flag.');st.stop()
st.error('CRPS-3 não é suspensão. É condição para abertura de análise técnico-administrativa, após garantias.')
labels={'mcn_validada':'MCN validada','maic_concluida':'MAIC concluída','escuta_realizada':'Escuta realizada','apoios_verificados':'Apoios ofertados/acessíveis verificados','responsabilidade_institucional':'Responsabilidade institucional verificada','justificativas_analisadas':'Justificativas analisadas'}
checks={k:st.checkbox(v) for k,v in labels.items()};ok,missing=crps3_allowed(checks)
if ok: st.success('Checklist mínimo satisfeito. CRPS-3 pode ser registrada por profissional competente, com fundamentação.')
else: st.warning('CRPS-3 bloqueada. Pendências: '+', '.join(labels[x] for x in missing))
next_action('Garantias em conferência','Concluir todas as verificações antes de qualquer avanço restritivo.')
st.subheader('Fluxo recursal');st.write('Parecer → Notificação → 1º recurso/reanálise → decisão técnica → recurso final → Comissão Paritária → decisão final → conferência → eventual execução')
