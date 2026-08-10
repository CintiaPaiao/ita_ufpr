# Refatoração 0.4 – Homologação, segurança e primeira versão de produção Streamlit

A versão 0.4 mantém o **Streamlit como camada de apresentação e deploy**, preservando a arquitetura de domínio e persistência independente da interface.

## Objetivos implementados

- autenticação PBKDF2 com usuários via Streamlit Secrets ou banco;
- desativação obrigatória das credenciais demo em `APP_ENV=production`;
- sessão com expiração e limite de tentativas por sessão;
- RBAC nas páginas;
- leitura de `DATABASE_URL` por variável de ambiente ou Streamlit Secrets;
- SQLite para desenvolvimento/homologação e PostgreSQL opcional/recomendado para implantação multiusuária persistente;
- pool e `pool_pre_ping` para banco servidor;
- checklist automático de prontidão para produção;
- backup institucional (Planilha Unificada + cópia SQLite quando aplicável);
- mecanismo controlado de retenção de logs técnicos;
- configuração XSRF/CORS e limitação de upload no Streamlit;
- rascunhos assistidos de comunicações, sem envio automático;
- painel de sensibilidade do IAL;
- painel agregado de auditoria de equidade;
- pipeline CI para compile/test/environment check;
- documentação de deploy no Streamlit;
- melhorias do workflow da ficha para reavaliação, CRPS e recurso.

## Limites preservados

A versão 0.4 não automatiza parecer profissional, persistência fundamentada, classificação CRPS, suspensão, decisão recursal ou decisão da Comissão. Parâmetros metodológicos ainda pendentes continuam configuráveis/bloqueáveis.
