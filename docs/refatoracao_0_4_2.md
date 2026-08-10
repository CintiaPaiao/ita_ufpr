# Refatoração 0.4.2 — Fluxo de inicialização e gestão de ciclos no Streamlit

## Objetivo

Eliminar a dependência operacional de scripts manuais para iniciar a aplicação em deploy Streamlit e tornar a gestão dos ciclos semestrais administrável pela própria interface.

## Implementações

- bootstrap automático do schema no startup;
- criação idempotente dos ciclos definidos em `configs/ciclos.yaml`;
- ausência de dependência de `load_sample_data.py` para produção;
- tela administrativa para criar, ativar, encerrar e reabrir ciclos;
- bloqueio de importação/processamento para ciclos encerrados;
- checklist de produção considera ausência de ciclos como falha crítica;
- em `APP_ENV=production`, SQLite local é tratado como falha crítica de persistência para deploy Streamlit;
- mensagem de inicialização informa quando ciclos foram criados automaticamente.

## Regra de produção no Streamlit

O Streamlit permanece como frontend/deploy. Para dados reais, a recomendação da versão 0.4.2 é usar PostgreSQL externo persistente por meio de `DATABASE_URL` nos Streamlit Secrets. SQLite permanece disponível para desenvolvimento e homologação temporária.
