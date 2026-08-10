# Homologação da compatibilidade com o template real do ITA 2025 – Refatoração 0.3

A refatoração 0.3 foi testada contra a planilha anonimizada fornecida no projeto, com 460 registros e 104 colunas no mesmo padrão operacional utilizado pela Calculadora ITA 2025.

Resultado do teste de integração realizado durante a geração desta versão:

- 460 estudantes importados para o universo do ciclo;
- 460 snapshots acadêmicos legados preservados;
- 89 registros de acompanhamento identificados nos blocos multiprofissionais embutidos na planilha;
- 58 fatores de proteção explícitos extraídos da coluna PROAFE, sem qualquer pontuação;
- 323 registros históricos do processo de 2025 preservados em tabela de legado;
- 2.300 resultados de MCN produzidos (cinco artigos por estudante);
- 460 resultados de IAL produzidos;
- 300 estudantes incluídos na lista preliminar quando `N=300`;
- 459 IAL parciais e 1 não calculável, consequência esperada da ausência, no template agregado, dos parâmetros necessários para calcular integralmente a progressão curricular sem presumir dados.

A planilha real não é distribuída no repositório/ZIP. O teste utiliza o arquivo somente no ambiente de homologação e registra apenas estatísticas agregadas.

## Interpretação

O template legado é suficiente para importar o universo, reproduzir os dados acadêmicos agregados disponíveis, calcular com segurança os componentes que possuem evidência e organizar a priorização preliminar. Entretanto, não contém todas as evidências exigidas pela metodologia atual para conclusão automática dos arts. 17, 20 e 21 ou para cobertura integral do componente de progressão do IAL. Nesses casos a aplicação devolve `DADO_PENDENTE`, `REQUER_CONFERENCIA` ou IAL parcial, em vez de presumir parâmetros.
