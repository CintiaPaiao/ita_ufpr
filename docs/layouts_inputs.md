# Layouts de arquivos de entrada

A versão 0.4.4 gera os layouts diretamente a partir do registro de bases (`configs/bases.yaml`). Isso evita manter documentação e código divergentes.

## Bases individuais

- SIGA_BENEFICIARIOS
- HISTORICO_ACADEMICO
- PARAMETROS_CURRICULARES
- DISCIPLINAS_OBRIGATORIAS
- TAXAS_APROVACAO_TURMAS
- INTEGRALIZACAO_TEMPO
- ACOMPANHAMENTO_P4E
- ACOMPANHAMENTO_PROAFE
- ACOMPANHAMENTO_CATRIM
- HISTORICO_AVALIACAO
- LEGADO_ITA_2025
- LEGADO_PLANILHA_COMPLETA
- FORMULARIO_CONTEXTUALIZACAO

Cada uma possui modelo próprio disponível na interface.

## Pacote legado

Além da planilha principal e do formulário, existe modelo próprio de workbook de acompanhamento, com abas de Serviço Social, Psicologia, Pedagogia, CAISE, CPPOVOS, CATRIM e PROAFE-CAS.

## Cabeçalhos

A aba `DICIONARIO` de cada modelo contém todos os aliases que o importador reconhece naquele momento. A aba `MODELO` utiliza o cabeçalho recomendado.
