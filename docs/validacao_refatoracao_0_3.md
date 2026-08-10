# Validação técnica da Refatoração 0.3

## Objetivo

Validar a compatibilidade da aplicação com o modelo de bases utilizado pela Calculadora ITA 2025, sem transportar para a nova metodologia os scores incompatíveis do legado.

## Validações executadas

- Compilação dos módulos Python: concluída sem erros.
- Migrações Alembic: `alembic upgrade head` executado com sucesso em banco SQLite temporário.
- Suíte automatizada: 26 testes aprovados e 0 falhas.
- Importação do modelo anonimizado da Planilha Completa utilizada no processo ITA: 460 registros importados e persistidos em banco temporário.
- Processamento do ciclo sobre a base de compatibilidade:
  - 460 estudantes processados;
  - 2.300 registros MCN, correspondentes aos cinco artigos por estudante;
  - 460 resultados IAL;
  - 300 registros de priorização, conforme parâmetro N do ciclo.

## Comportamento protetivo na base agregada legada

A Planilha Completa do ITA oferece vários dados acadêmicos agregados, mas não contém evidência suficiente para automatizar integralmente todos os critérios atuais. Por isso a aplicação não preenche lacunas por inferência:

- art. 17: `DADO_PENDENTE` quando não há detalhamento de disciplina obrigatória;
- art. 18: `PARAMETRO_NAO_CONFIRMADO` quando não há parâmetro curricular validado;
- art. 19: pode ser calculado diretamente quando quantidade matriculada e reprovações por frequência estão disponíveis;
- art. 20: `REQUER_CONFERENCIA` na compatibilidade agregada, pois a taxa observada do estudante não prova, sozinha, as exclusões normativas por cancelamento e taxa da turma;
- art. 21: `REQUER_CONFERENCIA` quando o tempo disponível é apenas o tempo bruto de vínculo e não o tempo computável validado.

O IAL pode ser calculado parcialmente quando os componentes R e F estão disponíveis. O componente P somente é produzido quando existirem parâmetros curriculares suficientes para seu cálculo, mantendo o resultado explicitamente identificado como parcial quando cabível.

## Regra de migração

O ITA legado, renda, classe socioeconômica e indicadores antigos de acompanhamento são preservados apenas para rastreabilidade histórica. Nenhum deles é convertido automaticamente em IAL, fator punitivo, CRPS ou decisão de suspensão.
