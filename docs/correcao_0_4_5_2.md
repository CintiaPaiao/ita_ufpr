# Correção 0.4.5.2

A v0.4.5.1 foi identificada como regressiva: o pacote havia sido reduzido e deixou de incluir dependências e partes importantes da jornada da v0.4.4.

A v0.4.5.2 foi reconstruída **sobre a árvore completa da v0.4.4**, preservando a importação validada e acrescentando as melhorias planejadas para 0.4.5.

## Correções principais

- restauração de SQLAlchemy, Alembic, Pandera, Plotly, dotenv e driver PostgreSQL no `requirements.txt`;
- preservação integral de `02_dados.py`, incluindo Pacote ITA 2025, base individual, status, processamento e histórico;
- preservação das páginas profissionais e administrativas da 0.4.4;
- nova página **Jornada do Ciclo**, baseada em dados reais do banco e indicando próxima ação;
- nova **Central de Configurações** para IAL, MCN, priorização, feature flags e catálogo de fatores;
- remoção de `use_container_width`, substituído pela API `width="stretch"` compatível com Streamlit atual;
- teste de integridade do release para impedir nova perda silenciosa do fluxo de importação;
- script de conferência das dependências essenciais.

## Regra para futuros releases

Nenhuma evolução de UX deve substituir a arquitetura da versão anterior por uma implementação simplificada. A evolução deve ocorrer incrementalmente sobre o release homologado.
