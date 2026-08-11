# Correção 0.4.5.1 — colisão do módulo `src.ui`

## Erro corrigido

No Streamlit Cloud foi observado:

`ImportError: cannot import name 'setup' from 'src.ui' (.../src/ui/__init__.py)`

A versão 0.4.5 continha `src/ui.py`, mas repositórios atualizados sobre versões
anteriores podiam conservar o diretório `src/ui/`. Quando arquivo e pacote
coexistiam, o Python podia resolver `src.ui` como o pacote antigo, que não
exportava `setup`/`next_action`.

## Solução

- `src.ui` passa a ser **um pacote único e explícito**;
- funções compartilhadas ficam em `src/ui/helpers.py`;
- `src/ui/__init__.py` exporta `setup` e `next_action` para compatibilidade;
- páginas usam `from src.ui.helpers import ...`, eliminando ambiguidade;
- `src/ui.py` foi removido;
- foi incluído teste de regressão para a importação.

## Atualização do GitHub

Recomenda-se substituir integralmente os arquivos da versão anterior, e não
apenas copiar os novos por cima. Se fizer merge manual, remova o antigo
`src/ui.py` e confirme que o diretório `src/ui/` contém os arquivos desta versão.
