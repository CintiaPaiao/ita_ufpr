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

## Cobertura acrescentada na versão 0.4

| ID | Requisito | Status | Arquivo/módulo | Verificação |
|---|---|---|---|---|
| R33 | Deploy Streamlit em modo produção | Implementado | `.streamlit/`, `app.py` | checklist de prontidão |
| R34 | Senhas PBKDF2 | Implementado | `src/security/passwords.py` | `test_passwords_v04.py` |
| R35 | Streamlit Secrets | Implementado | `src/config/runtime.py` | configuração/documentação |
| R36 | RBAC por página | Implementado | `src/ui/common.py`, `pages/` | revisão de rotas |
| R37 | Sessão expirada/limite de tentativas | Implementado | `src/security/auth.py` | revisão funcional |
| R38 | PostgreSQL opcional | Implementado | `src/db/session.py`, requirements | configuração `DATABASE_URL` |
| R39 | Checklist de produção | Implementado | `readiness_service.py`, página 24 | `test_readiness_v04.py` |
| R40 | Backup institucional | Implementado | `backup_service.py`, página 24 | `test_backup_v04.py` |
| R41 | Retenção de logs | Implementado assistido | `retention_service.py` | exige confirmação humana |
| R42 | Sensibilidade IAL | Implementado | `sensitivity_service.py`, página 04a | `test_sensitivity_v04.py` |
| R43 | Auditoria de equidade agregada | Implementado | `equity_service.py`, página 22a | revisão funcional |
| R44 | Comunicações em rascunho | Implementado | `communication_service.py`, página 20a | sem envio automático |
| R45 | GitHub CI | Implementado | `.github/workflows/ci.yml` | compile + pytest + environment |
| R46 | Configuração endurecida do Streamlit | Implementado | `.streamlit/config.toml` | XSRF/CORS/error details |
| R47 | Workflow ampliado reavaliação/CRPS/recurso | Implementado | `case_service.py` | `test_case_workflow_v04.py` |

| R33 | Bootstrap automático do schema/ciclos | Implementado 0.4.3 | src/services/bootstrap_service.py + app.py | test_bootstrap_v042.py | Sem dados sintéticos |
| R34 | Gestão de ciclos pela interface | Implementado 0.4.3 | pages/23_administracao.py | test_cycle_management_v042.py | Criar/ativar/encerrar/reabrir |
| R35 | Produção Streamlit sem scripts manuais | Implementado 0.4.3 | app.py | teste bootstrap | init/load_sample não obrigatórios |
| R36 | Bloqueio de ciclo encerrado | Implementado 0.4.3 | pages/02_dados.py | revisão/teste serviço | Evita novas operações |
| R37 | Persistência externa crítica em produção Streamlit | Implementado 0.4.3 | readiness_service.py | test_readiness_v042.py | PostgreSQL recomendado |
