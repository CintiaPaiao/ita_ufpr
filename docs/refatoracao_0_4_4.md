# Refatoração 0.4.4 — Modelos de todas as bases de entrada

## Objetivo

Eliminar dúvidas sobre o layout dos arquivos de input obrigatórios, opcionais e de compatibilidade legada.

## Implementado

A página **Bases, Importação e Processamento do Ciclo** passa a oferecer:

1. na aba **Pacote da Calculadora ITA 2025**, downloads separados para:
   - Planilha principal / PLANILHA COMPLETA;
   - Workbook de acompanhamentos por equipe;
   - Formulário de contextualização;

2. na aba **Importar base individual**:
   - botão **Baixar modelo desta base** para todo tipo cadastrado em `configs/bases.yaml`;
   - botão **Baixar todos os modelos de input**, gerando um ZIP com todos os XLSX.

## Estrutura de cada XLSX

- `MODELO`: cabeçalhos recomendados + uma linha de exemplo sintético;
- `DICIONARIO`: campo canônico, obrigatoriedade mínima, tipo, descrição, aliases reconhecidos e exemplo;
- `INSTRUCOES`: finalidade, granularidade, tratamento de dados ausentes, ciclo e cuidados de LGPD.

## Regra de compatibilidade

O cabeçalho exibido no `MODELO` é selecionado entre os aliases já reconhecidos pelo importador da aplicação. Assim, o próprio arquivo de modelo é importável sem renomear colunas.

## Atenção

A linha preenchida é exclusivamente exemplo sintético e deve ser removida/substituída quando a base real for preparada.
