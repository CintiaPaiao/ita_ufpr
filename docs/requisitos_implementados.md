# Cobertura funcional v0.4.5

| Requisito | Status | Evidência |
|---|---|---|
| Assistente de ciclo | IMPLEMENTADO | `pages/01_Jornada_do_Ciclo.py` |
| Validação orientada à correção | IMPLEMENTADO | `validate_df()` + página Jornada |
| Central de Configurações | IMPLEMENTADO | `pages/02_Central_de_Configuracoes.py` |
| Explicabilidade MCN/IAL | IMPLEMENTADO | `pages/03_MCN_IAL_Explicavel.py` |
| Congelamento/hash | IMPLEMENTADO | `freeze_cycle()` |
| Status de ausências | IMPLEMENTADO/PARCIAL | estados DADO_PENDENTE/NAO_CALCULAVEL/REQUER_CONFERENCIA |
| Ficha/timeline | IMPLEMENTADO/PARCIAL | fila/ficha + registros profissionais |
| QA/observabilidade | IMPLEMENTADO/PARCIAL | painel de qualidade |
| Auditoria de equidade | ESTRUTURA/FLAG | não usa atributos para score |
| RBAC | PENDENTE PARA PRODUÇÃO | arquitetura indicada; não afirmar segurança de produção |
| MCN 17–21 | PARCIAL | 19/20 executáveis; 17/18/21 dependem de fontes/regras institucionais |
| IAL configurável | IMPLEMENTADO | pesos/cobertura/faixas em configuração |
| MAIC/MNA/PIAAP/manutenção/monitoramento | IMPLEMENTADO COMO REGISTRO TRANSACIONAL | sem decisão automática |
| Reavaliação | IMPLEMENTADO COMO FASE/REGISTRO | nova seleção deve ser observada no fluxo oficial |
| CRPS | IMPLEMENTADO COM TRAVA | checklist obrigatório para CRPS-3 |
| Recursos/Comissão | IMPLEMENTADO COMO FLUXO/FLAG | parâmetros institucionais permanecem configuráveis |
| Docker | IMPLEMENTADO | Dockerfile/compose |
| Testes | IMPLEMENTADO | `tests/test_core.py` |
