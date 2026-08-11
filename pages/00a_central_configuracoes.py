from __future__ import annotations

from copy import deepcopy
import streamlit as st

from src.ui.common import page_setup, safe_exception
from src.ui.ux import info_card
from src.services.configuration_service import current_configuration, save_configuration, validate_configuration

page_setup('Central de Configurações – v0.4.5.2', allowed_roles=('ADMIN','CHEFIA'))
cfg=current_configuration()

info_card('Governança da configuração',
          'Parâmetros metodológicos devem ser pactuados e versionados. A Central permite parametrizar o que é mapeável, mas não transforma lacunas institucionais em regras automáticas. Em Streamlit Cloud, alterações de arquivos podem não sobreviver a um redeploy; para produção definitiva, mantenha os valores no repositório/versionamento institucional.', icon='⚙️')

with st.form('central_cfg'):
    st.subheader('1. IAL')
    c1,c2,c3=st.columns(3)
    cfg['ial']['weights']['rendimento']=c1.number_input('Peso rendimento (%)',0.0,100.0,float(cfg['ial']['weights']['rendimento']),1.0)
    cfg['ial']['weights']['frequencia']=c2.number_input('Peso frequência (%)',0.0,100.0,float(cfg['ial']['weights']['frequencia']),1.0)
    cfg['ial']['weights']['progressao']=c3.number_input('Peso progressão (%)',0.0,100.0,float(cfg['ial']['weights']['progressao']),1.0)
    d1,d2,d3=st.columns(3)
    cfg['ial']['coverage']['partial_minimum']=d1.number_input('Cobertura mínima parcial (%)',0.0,100.0,float(cfg['ial']['coverage']['partial_minimum']),1.0)
    cfg['ial']['parameters']['trend_reference_pp']=d2.number_input('Referência de tendência (p.p.)',1.0,100.0,float(cfg['ial']['parameters']['trend_reference_pp']),1.0)
    cfg['ial']['parameters']['trend_modifier']=d3.number_input('Modificador de tendência',0.0,1.0,float(cfg['ial']['parameters']['trend_modifier']),0.01)
    cfg['ial']['parameters']['progress_gap_reference']=st.number_input('Referência do gap de progressão',0.05,1.0,float(cfg['ial']['parameters']['progress_gap_reference']),0.05)

    st.markdown('**Faixas do IAL**')
    new_bands=[]
    for i,b in enumerate(cfg['ial']['bands']):
        a,bx,c=st.columns([2,2,6])
        mn=a.number_input(f'Mín. faixa {i+1}',0.0,100.0,float(b['min']),0.1,key=f'bmin{i}')
        mx=bx.number_input(f'Máx. faixa {i+1}',0.0,100.0,float(b['max']),0.1,key=f'bmax{i}')
        label=c.text_input(f'Rótulo faixa {i+1}',value=str(b['label']),key=f'blab{i}')
        new_bands.append({'min':mn,'max':mx,'label':label})
    cfg['ial']['bands']=new_bands

    st.subheader('2. MCN / parâmetros de cálculo')
    c1,c2,c3=st.columns(3)
    cfg['mcn']['art20']['minimum_student_approval_pct']=c1.number_input('Art. 20 — aprovação mínima (%)',0.0,100.0,float(cfg['mcn']['art20']['minimum_student_approval_pct']),1.0)
    cfg['mcn']['art20']['exclude_class_approval_below_pct']=c2.number_input('Art. 20 — excluir turma abaixo de (%)',0.0,100.0,float(cfg['mcn']['art20']['exclude_class_approval_below_pct']),1.0)
    cfg['mcn']['art21']['max_regular_factor']=c3.number_input('Art. 21 — multiplicador máximo',1.0,3.0,float(cfg['mcn']['art21']['max_regular_factor']),0.1)
    cfg['mcn']['art18']['automatic_minimum_evidence_grade']=st.selectbox('Art. 18 — grau mínimo de evidência para automação', ['A','B','C','D'], index=['A','B','C','D'].index(str(cfg['mcn']['art18']['automatic_minimum_evidence_grade']).upper()))
    st.caption('Limites do art. 19 estão ligados à regra normativa e não devem ser alterados apenas por conveniência operacional.')

    st.subheader('3. Priorização e capacidade operacional')
    c1,c2,c3=st.columns(3)
    cfg['priorizacao']['selection']['n_cases']=c1.number_input('N de casos para seleção',1,10000,int(cfg['priorizacao']['selection']['n_cases']),10)
    cfg['priorizacao']['selection']['n_professionals']=c2.number_input('Número de profissionais',1,100,int(cfg['priorizacao']['selection']['n_professionals']),1)
    cfg['priorizacao']['selection']['cases_per_professional']=c3.number_input('Referência de casos/profissional',1,1000,int(cfg['priorizacao']['selection']['cases_per_professional']),1)

    st.subheader('4. Feature flags')
    features=cfg['features'].get('features',{})
    cols=st.columns(2)
    for i,(k,v) in enumerate(list(features.items())):
        features[k]=cols[i%2].toggle(k,value=bool(v),key=f'feat_{k}')
    cfg['features']['features']=features

    st.subheader('5. Catálogo de fatores de proteção')
    factors=cfg['fatores_protecao'].get('factors',[])
    txt=st.text_area('Um fator por linha',value='\n'.join(factors),height=180)
    cfg['fatores_protecao']['factors']=[x.strip() for x in txt.splitlines() if x.strip()]

    st.subheader('6. Profissionais')
    st.caption('A edição completa de nomes/territórios continua disponível em Administração; aqui é exibida a configuração atual.')
    st.json(cfg['servidores'])

    save=st.form_submit_button('SALVAR CONFIGURAÇÃO',type='primary',width='stretch')

if save:
    errors=validate_configuration(cfg)
    if errors:
        for e in errors: st.error(e)
    else:
        try:
            save_configuration(cfg)
            st.success('Configuração salva e aplicada ao processo atual. Para produção permanente no Streamlit, versionar também os arquivos de configuração no repositório.')
        except Exception as exc:
            safe_exception(exc,prefix='Não foi possível salvar a configuração.')

with st.expander('Parâmetros que dependem de decisão institucional'):
    st.markdown('''
    - pesos e faixas definitivos do IAL;
    - inventário completo do art. 18;
    - fonte oficial das taxas de turma do art. 20;
    - tratamento integral do tempo computável no art. 21;
    - protocolo definitivo do PIAAP;
    - prazos/competências do fluxo recursal e Comissão Paritária.

    Esses pontos devem permanecer configuráveis, bloqueados ou documentados como pendentes enquanto não houver pactuação institucional.
    ''')
