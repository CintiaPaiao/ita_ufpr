# Refatoração 0.3 – Integração real das bases e automação da jornada

## Objetivo
Tornar a aplicação compatível com as bases reais usadas pela Calculadora ITA 2025, sem transportar a lógica punitiva ou o score agregado antigo.

## Implementado
- importação em pacote da PLANILHA COMPLETA;
- reconhecimento automático da aba `PLANILHA COMPLETA`/`Sheet1`;
- mapeamento dos cabeçalhos reais do legado;
- snapshot acadêmico agregado por estudante/ciclo;
- importação das abas de Serviço Social, Psicologia e Pedagogia, além de setores adicionais reconhecidos;
- formulário opcional com preservação do registro bruto e fatores apenas quando estruturados;
- processamento MCN/IAL com fallback seguro ao snapshot legado;
- Art.19 calculável quando a quantidade de RF está disponível;
- Art.17, Art.20 e Art.21 protegidos contra inferências quando a base agregada não oferece evidência suficiente;
- IAL parcial a partir de rendimento e frequência quando progressão não possui parâmetros confirmados;
- ficha pré-análise automática;
- próxima ação automática na fila/ficha;
- reavaliação automática entre ciclos armazenados;
- persistência quantitativa separada da fundamentada.

## Breaking changes metodológicas preservadas
O antigo ITA, renda e acompanhamento não são usados como score do novo sistema. O ITA legado pode ser armazenado apenas como informação histórica.
