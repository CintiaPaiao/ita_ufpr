# Importação operacional das bases

A versão 0.2.0 implementa o circuito **arquivo → validação → registro → SQLite → processamento do ciclo**.

## Uso

1. Abra `Bases, Importação e Processamento do Ciclo`.
2. Selecione o ciclo.
3. Selecione o tipo de base.
4. Faça upload de XLSX/XLS/CSV.
5. Confira o mapeamento de colunas e a prévia padronizada.
6. Clique em **VALIDAR E REGISTRAR BASE**.
7. Consulte a aba **Status das bases**.
8. Após registrar as bases necessárias, clique em **PROCESSAR CICLO**.

O processamento gera MCN, IAL e priorização preliminar. Contextualização, MAIC, MNA, CRPS e decisões continuam profissionais.

## Tipos de base

O catálogo e aliases estão em `configs/bases.yaml`. Isso permite adaptar cabeçalhos sem alterar a lógica do domínio.

## Substituição e versionamento

Cada upload é registrado em `arquivos_importados`, com hash SHA-256, usuário, ciclo, linhas e status. A opção de substituição remove/regenera os registros correspondentes daquela base, preservando o histórico de importações e os logs.

## Congelamento

Depois de validar a versão das bases, o ciclo pode ser congelado. Um ciclo congelado não aceita novas importações até que haja procedimento institucional de nova versão.

## Homologação incompleta

A interface permite processar com bases obrigatórias pendentes somente em modo explícito de homologação. Nessas situações, MCN/IAL podem resultar em `DADO_PENDENTE`, `REQUER_CONFERENCIA`, `PARAMETRO_NAO_CONFIRMADO` ou `NAO_CALCULAVEL`.
