# Refatoração 0.4.3 – Correção do bootstrap no Streamlit multipágina

## Erro corrigido

`sqlite3.OperationalError: no such table: ciclos` ao abrir diretamente uma página em `pages/`.

## Causa

O bootstrap de schema/ciclos estava concentrado em `app.py`. No mecanismo multipágina do Streamlit, uma página pode ser executada diretamente sem que o corpo de `app.py` tenha sido executado previamente. A página 02 abria uma sessão e chamava `ensure_default_cycles()`, mas a tabela `ciclos` ainda não existia.

## Correção

1. `session_scope()` agora chama `ensure_schema()` antes de criar qualquer sessão.
2. `ensure_schema()` é idempotente e protegido por `RLock`.
3. `page_setup()` executa `bootstrap_application()` em toda rota Streamlit, garantindo schema e ciclos.
4. O diretório do SQLite é criado automaticamente quando necessário.
5. Foi adicionado teste de regressão que reproduz o padrão exato da página 02 sobre banco completamente vazio.

A correção não altera MCN, IAL, priorização ou regras metodológicas.
