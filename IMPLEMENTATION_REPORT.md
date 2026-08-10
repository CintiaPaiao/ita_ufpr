# Relatório de Implementação – versão 0.4.2

## Classificação da entrega

Primeira versão **preparada para produção com deploy Streamlit**, mantendo execução local e Docker. A aplicação está tecnicamente estruturada para SQLite ou PostgreSQL e possui controles de produção que não existiam nas versões 0.1–0.3.

## Núcleo funcional

- importação real e compatibilidade com o modelo da Calculadora ITA 2025;
- persistência relacional;
- MCN arts. 17–21 com estados protetivos de dado insuficiente;
- IAL configurável e cobertura;
- fatores de proteção em quatro fontes sem score;
- acompanhamentos;
- priorização N em camadas;
- validação humana e distribuição;
- ficha pré-análise/fila/ficha individual;
- contextualização, atendimento, MAIC, MNA, PIAAP, manutenção e monitoramento;
- reavaliação longitudinal automática com análise profissional separada;
- CRPS com gate procedimental;
- recursos e Comissão;
- exportações e logs.

## Produção 0.4

Implementados: PBKDF2, Streamlit Secrets, usuários via secrets/banco, RBAC, sessão expirada, limite de tentativas, modo demo bloqueado em produção, PostgreSQL opcional, pool/healthcheck lógico, checklist de prontidão, backup, retenção de logs, CI, endurecimento Streamlit, painel de sensibilidade, auditoria de equidade e rascunhos de comunicação.

## Homologação necessária antes de uso institucional

A configuração `APP_ENV=production` não substitui homologação institucional. É necessário validar bases reais, parâmetros dos arts. 18/20/21, pesos/faixas do IAL, perfis de acesso, retenção, backup e infraestrutura de banco.

## Itens deliberadamente não automatizados

Parecer profissional, persistência fundamentada, CRPS, suspensão, decisão de recurso e decisão da Comissão.

## Deploy

O frontend continua integralmente em Streamlit. Para uma implantação com cinco profissionais gravando simultaneamente, o pacote aceita PostgreSQL externo mantendo o Streamlit como aplicação.

## Testes

A entrega inclui suíte de regressão das versões anteriores mais testes 0.4 para hashing, readiness, sensibilidade, workflow e exportação.


## Validação desta entrega

31 testes aprovados; Alembic aprovado; homologação da planilha anonimizada ITA 2025 com 460 estudantes, 2.300 MCN, 460 IAL e 300 priorizações. O smoke visual Streamlit deve ser executado no ambiente de deploy, pois Streamlit não estava instalado no runtime de construção desta entrega.

## Atualização 0.4.2

A versão 0.4.2 elimina a dependência de inicialização manual para deploy Streamlit. O startup cria o schema e os ciclos padrão automaticamente, sem carregar estudantes fictícios. A administração de ciclos passou para a interface e o checklist de prontidão classifica SQLite local como inadequado para produção Streamlit com dados reais, mantendo PostgreSQL externo como backend recomendado.
