# Segurança e LGPD – versão 0.4

## Controles implementados

- autenticação com PBKDF2-SHA256;
- usuários configuráveis por Streamlit Secrets ou banco;
- RBAC por módulo;
- expiração de sessão;
- limite de tentativas por sessão;
- modo demo bloqueado em produção;
- secrets fora do Git;
- mensagens de erro reduzidas em produção;
- logs de alterações críticas;
- minimização específica na Comissão;
- auditoria agregada de equidade;
- backup com alerta de conteúdo sensível;
- expurgo técnico somente mediante confirmação.

## Controles institucionais ainda necessários

A implantação real exige definição institucional de: responsáveis pelo tratamento, matriz final de acesso, período de retenção, rotina de backup, local autorizado de armazenamento, procedimento de incidente e eventual integração de identidade institucional.

## Regra de minimização

Diagnósticos, relatos detalhados e documentos comprobatórios não devem circular em dashboards gerais quando um marcador funcional/contextual suficiente atende à finalidade profissional.
