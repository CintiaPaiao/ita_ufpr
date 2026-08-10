## 0.4.0
- Segurança PBKDF2 e RBAC.
- Streamlit Secrets e modo production.
- PostgreSQL opcional.
- Prontidão, backup e retenção.
- Sensibilidade IAL e auditoria de equidade.
- Comunicações assistidas.
- CI e documentação de deploy Streamlit.

## 0.3.0
- Compatibilidade com PLANILHA COMPLETA e planilhas de atendimento da Calculadora ITA 2025.
- Snapshot acadêmico legado.
- Fallback MCN/IAL seguro.
- Ficha pré-análise e próxima ação automáticas.
- Reavaliação automática entre ciclos.

# Changelog

## 0.4.1
- Corrigido módulo ausente `src.services.cycle_service`, necessário ao congelamento do ciclo e à página de importação/processamento.
- Adicionada verificação estática de imports de serviços.

## 0.1.0
- Fundação Streamlit/SQLAlchemy/SQLite.
- MCN, IAL, proteção, acompanhamentos e priorização.
- Jornada profissional até recursos/Comissão.
- Exportação de 19 abas.
- Testes básicos e documentação.

## 0.2.0
- Importação operacional e persistência das planilhas.
- Catálogo de bases/aliases em YAML.
- Registro de arquivo/hash/ciclo/usuário.
- Painel de status das bases.
- Pipeline de processamento do ciclo (MCN + IAL + priorização).
- Congelamento de versão do ciclo.
- Testes de integração da importação e processamento.

## 0.3.0
- Compatibilidade operacional com a planilha completa/unificada utilizada pela Calculadora ITA 2025, inclusive quando a aba se chama `Sheet1`.
- Reconhecimento do perfil de colunas do legado e diagnóstico de cobertura antes da importação.
- Extração automática dos blocos de Serviço Social, Psicologia, Pedagogia, CAISE, CPPOVOS e CATRIM quando efetivamente preenchidos na própria planilha unificada.
- Conversão de marcadores explícitos da coluna PROAFE em fatores de proteção sem score.
- Preservação dos registros de parecer/recurso de 2025 em tabela histórica própria, sem convertê-los em IAL, CRPS ou decisão atual.
- Reavaliação passa a recuperar automaticamente MCN/IAL anteriores, MAIC, MNA, PIAAP, ações, monitoramentos, acompanhamentos e atendimentos do ciclo anterior.
- Ficha pré-análise ampliada com fontes dos fatores de proteção e registro legado identificado.
- Homologação estrutural contra a planilha real anonimizada de 2025 fornecida para desenvolvimento.

## 0.4.3
- Bootstrap automático do banco e dos ciclos semestrais no startup.
- Removida dependência de `scripts/init_db.py` e `load_sample_data.py` para iniciar em produção.
- Gestão de ciclos na interface ADMIN: criar, ativar, encerrar e reabrir.
- Bloqueio de operações em ciclos encerrados.
- Checklist de prontidão endurecido para persistência em deploy Streamlit.
- Documentação específica do fluxo de produção no Streamlit.
