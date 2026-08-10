# Validação técnica – Refatoração 0.4

## Suíte automatizada

- `python -m compileall -q .`: aprovado.
- `pytest -q`: **31 testes aprovados**, 0 falhas e 0 avisos após ajuste de timestamps UTC.
- `alembic upgrade head`: executado com sucesso em SQLite.

## Homologação com a base real anonimizada no modelo ITA 2025

Arquivo utilizado: `Cópia de Analise_Probem_COMPLETA FINAL SEM NOME E DADOS.xlsx`.

Resultado do pipeline 0.4:

- 460 estudantes importados;
- 460 estudantes processados;
- 2.300 registros MCN (5 artigos por estudante);
- 460 resultados de IAL;
- 300 registros de priorização, conforme N configurado;
- modo de compatibilidade legada identificado corretamente;
- nenhuma conversão do ITA legado em IAL/CRPS.

## Validação de produção

A configuração de produção foi implementada, mas o smoke test visual do servidor Streamlit não foi executado neste ambiente porque o pacote `streamlit` não está instalado na imagem de execução usada para a refatoração. O `requirements.txt` contém a dependência e o repositório inclui checklist/CI para o ambiente de deploy.

Antes do uso com dados reais no endereço definitivo, executar o checklist **Produção e Prontidão** com os secrets e banco do ambiente de implantação.
