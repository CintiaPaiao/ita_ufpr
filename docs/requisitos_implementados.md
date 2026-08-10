# Requisitos implementados

| ID | Requisito | Status | Módulo | Observação |
|---|---|---|---|---|
| R01 | SQLite + SQLAlchemy | Implementado | src/db, src/models | Preparado para PostgreSQL |
| R02 | MCN arts. 17–21 | Implementado | src/domain/mcn | Art.18 pode exigir conferência |
| R03 | IAL 40/35/25 configurável | Implementado | src/domain/ial | Parâmetros de teste |
| R04 | Dado ausente ≠ zero | Implementado | MCN/IAL | Usa `None`/estados |
| R05 | Quatro fontes de proteção | Implementado no modelo | fatores_protecao | Sem score |
| R06 | Acompanhamentos | Implementado | acompanhamentos | Sem score |
| R07 | Priorização em camadas/N | Implementado | prioritization | Validação humana |
| R08 | Distribuição | Implementado | distribuições | Ajustável |
| R09 | Streamlit multipágina | Implementado | pages | 23 páginas |
| R10 | Ficha individual | Implementado | page 10 | Abas internas |
| R11 | Contextualização | Implementado | page 11 | Não resposta não penaliza |
| R12 | Atendimento | Implementado | page 12 | Registro profissional |
| R13 | MAIC/MNA/PIAAP | Implementado | pages 13–15 | Sem conclusão automática |
| R14 | Manutenção/Monitoramento | Implementado | pages 16–17 | Ações estudante/instituição |
| R15 | Reavaliação | Implementado | page 18 | Comparação assistida |
| R16 | CRPS com gate | Implementado | page 19 | Não deriva do IAL |
| R17 | Recursos/Comissão | Implementado | pages 20–21 | Comissão minimizada |
| R18 | Auditoria | Implementado | logs/page 22 | Painel básico |
| R19 | Exportação 19 abas | Implementado | exports/page 23 | Inclui dicionário |
| R20 | RBAC básico | Implementado MVP | security | SSO pendente |
| R21 | Alembic | Implementado | database/migrations | Schema inicial |
| R22 | Docker | Implementado | Dockerfile/compose | Usuário não-root |
| R23 | Dados sintéticos | Implementado | load_sample_data.py | 30 estudantes |
| R24 | Sensibilidade IAL | Parcial | config | UI avançada pendente |
| R25 | Google Drive API | Bloqueado/configurável | ingestion | Depende credencial institucional |
| R26 | Auditoria de equidade avançada | Parcial | page 22 | Depende base real/minimização |
