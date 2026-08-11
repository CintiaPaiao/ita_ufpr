from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import func, select

from src.ui.common import page_setup
from src.ui.ux import info_card, step_strip
from src.db.session import session_scope
from src.models.models import (
    Cycle, ImportedFile, MCNResult, IALResult, Prioritization, Allocation,
    Contextualization, Attendance, MAIC, MNA, PIAAP, Maintenance,
    Monitoring, Reassessment, CRPS, Appeal,
)
from src.services.base_status_service import base_status, required_ready
from src.services.bootstrap_service import ensure_default_cycles

page_setup('Jornada do Ciclo – v0.4.5.2')

with session_scope() as s:
    ensure_default_cycles(s)
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
if not cycles:
    st.error('Nenhum ciclo disponível. Verifique a inicialização do banco.'); st.stop()

codes=[c.codigo for c in cycles]
cycle_code=st.selectbox('Ciclo de trabalho', codes, index=len(codes)-1)
cycle=next(c for c in cycles if c.codigo==cycle_code)

with session_scope() as s:
    cycle_db=s.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    status_rows=base_status(s,cycle_code)
    ready,missing=required_ready(s,cycle_code)
    cid=cycle_db.id
    def count(model, *conds):
        stmt=select(func.count()).select_from(model)
        if hasattr(model,'cycle_id'):
            stmt=stmt.where(model.cycle_id==cid)
        for c in conds: stmt=stmt.where(c)
        return s.scalar(stmt) or 0
    metrics={
        'imports': s.scalar(select(func.count()).select_from(ImportedFile).where(ImportedFile.cycle_code==cycle_code)) or 0,
        'mcn': count(MCNResult), 'ial':count(IALResult),
        'priorizados': count(Prioritization, Prioritization.pre_selecionado==True),
        'selecionados': count(Prioritization, Prioritization.selecionado_final==True),
        'distribuidos': count(Allocation), 'contextualizacoes':count(Contextualization),
        'atendimentos':count(Attendance), 'maic':count(MAIC), 'mna':count(MNA),
        'piaap':count(PIAAP), 'manutencoes':count(Maintenance), 'monitoramentos':count(Monitoring),
        'reavaliacoes':count(Reassessment), 'crps':count(CRPS), 'recursos':count(Appeal),
    }

formal_valid = ready
processed = metrics['ial']>0 and metrics['mcn']>0
reviewed = metrics['priorizados']>0
selected = metrics['selecionados']>0
allocated = metrics['distribuidos']>0
analyzed = metrics['maic']>0 or metrics['atendimentos']>0
monitored = metrics['monitoramentos']>0
reassessed = metrics['reavaliacoes']>0
frozen = cycle.frozen_at is not None

states=[
    ('Preparar','done'), ('Modelos','done'),
    ('Importar','done' if metrics['imports'] else 'current'),
    ('Validar','done' if formal_valid else ('current' if metrics['imports'] else 'pending')),
    ('Congelar','done' if frozen else ('current' if formal_valid else 'pending')),
    ('Processar','done' if processed else ('current' if (formal_valid or metrics['imports']) else 'pending')),
    ('Revisar','done' if reviewed else ('current' if processed else 'pending')),
    ('Selecionar','done' if selected else ('current' if reviewed else 'pending')),
    ('Distribuir','done' if allocated else ('current' if selected else 'pending')),
    ('Analisar','done' if analyzed else ('current' if allocated else 'pending')),
    ('Monitorar','done' if monitored else ('current' if analyzed else 'pending')),
    ('Reavaliar','done' if reassessed else ('pending' if not monitored else 'current')),
]
step_strip(states)

c1,c2,c3,c4=st.columns(4)
c1.metric('Bases importadas', metrics['imports'])
c2.metric('MCN / IAL', f"{metrics['mcn']} / {metrics['ial']}")
c3.metric('Selecionados finais', metrics['selecionados'])
c4.metric('Casos distribuídos', metrics['distribuidos'])

if cycle.status=='ENCERRADO':
    info_card('Ciclo encerrado','O ciclo está encerrado administrativamente. Novas importações e processamento devem permanecer bloqueados.',icon='🔒')
elif not metrics['imports']:
    info_card('Próxima ação','Abra **Bases, Importação e Processamento** e carregue o Pacote ITA 2025 ou uma base individual.',icon='➡️')
elif not formal_valid:
    info_card('Próxima ação',f"Complete ou confira as bases formais pendentes: <b>{', '.join(missing) if missing else 'ver status das bases'}</b>. Para homologação, use o modo compatível somente quando metodologicamente adequado.",icon='➡️')
elif not frozen:
    info_card('Próxima ação','Revise a qualidade das bases. Quando a versão estiver pronta para processamento oficial, realize o congelamento técnico do ciclo.',icon='➡️')
elif not processed:
    info_card('Próxima ação','Execute **Processar ciclo** para gerar MCN, IAL e priorização preliminar.',icon='➡️')
elif not selected:
    info_card('Próxima ação','Revise a priorização preliminar e valide a seleção final pela equipe.',icon='➡️')
elif not allocated:
    info_card('Próxima ação','Distribua os casos entre os profissionais considerando continuidade, território e complexidade.',icon='➡️')
elif not analyzed:
    info_card('Próxima ação','Inicie a contextualização/escuta e registre a análise profissional do caso.',icon='➡️')
else:
    info_card('Situação do ciclo','A jornada está em execução profissional. Consulte fila, monitoramento, reavaliação e garantias conforme a fase de cada caso.',icon='✅')

st.subheader('Status das bases')
st.dataframe(pd.DataFrame(status_rows), width='stretch', hide_index=True)

st.subheader('Jornada profissional')
rows=[
    ['Contextualizações',metrics['contextualizacoes']],['Atendimentos',metrics['atendimentos']],
    ['MAIC',metrics['maic']],['MNA',metrics['mna']],['PIAAP',metrics['piaap']],
    ['Manutenções',metrics['manutencoes']],['Monitoramentos',metrics['monitoramentos']],
    ['Reavaliações',metrics['reavaliacoes']],['CRPS',metrics['crps']],['Recursos',metrics['recursos']],
]
st.dataframe(pd.DataFrame(rows,columns=['Etapa','Registros']), width='stretch', hide_index=True)

with st.expander('Como interpretar esta página?'):
    st.markdown('''
    - A jornada é **orientativa** e não substitui a metodologia institucional.
    - Uma etapa marcada como concluída significa que há registros correspondentes; não significa que todos os casos do ciclo terminaram a etapa.
    - **Congelamento técnico** registra a versão das bases e não é o mesmo que encerrar o ciclo.
    - O sistema não deve liberar decisões restritivas apenas por resultado de MCN ou IAL.
    ''')
