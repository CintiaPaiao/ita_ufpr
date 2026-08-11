# Migração 0.4.5.1 → 0.4.5.2

A atualização deve ser feita por **substituição limpa do repositório**, porque a v0.4.5.1 continha uma árvore simplificada e arquivos que não fazem parte da arquitetura restaurada.

## Antes de copiar a 0.4.5.2

Remova a árvore antiga da v0.4.5.1 ou faça um novo branch/commit substituindo todo o conteúdo.

Arquivos/páginas da 0.4.5.1 que não devem permanecer como duplicatas:

- `src/core.py`
- `pages/01_Jornada_do_Ciclo.py`
- `pages/02_Central_de_Configuracoes.py`
- `pages/03_MCN_IAL_Explicavel.py`
- `pages/04_Fila_e_Ficha.py`
- `pages/05_CRPS_Recursos.py`
- `pages/06_Qualidade_Auditoria.py`

A v0.4.5.2 possui a árvore completa da v0.4.4 e as novas páginas:

- `pages/00_jornada_ciclo.py`
- `pages/00a_central_configuracoes.py`

## Streamlit Community Cloud

Depois do commit:

1. confirme que `requirements.txt` está na raiz do repositório;
2. confirme que ele contém `SQLAlchemy`;
3. faça **Reboot app** ou redeploy;
4. se o Cloud mantiver cache do build antigo, force novo deploy por um commit adicional.
