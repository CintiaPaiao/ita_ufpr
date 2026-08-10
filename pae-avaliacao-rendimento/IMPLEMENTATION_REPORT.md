# Relatório de Implementação

## Estado

MVP funcional com arquitetura Streamlit + SQLAlchemy + SQLite. Não reproduz o ITA 2025 como score global.

## Implementado

Banco relacional, migrations, ingestão Excel/CSV, normalização/validação de GRR, MCN, IAL configurável, fatores de proteção sem score, acompanhamentos, priorização por camadas, validação humana, distribuição, dashboards, fila, ficha individual, contextualização, atendimento, MAIC, MNA, PIAAP, manutenção, monitoramento, reavaliação, CRPS com trava, recursos, Comissão, auditoria, exportação, autenticação MVP, testes, Docker e documentação.

## Parcial / dependente de pactuação

- UI avançada de sensibilidade do IAL.
- Auditoria de equidade avançada.
- Integração Google Drive API.
- Importadores específicos para cada cabeçalho institucional real.
- Inventário final do art.18, regras finais do art.21 e fonte institucional das taxas do art.20.
- SSO institucional e política definitiva de retenção.

## Breaking changes metodológicas

Vulnerabilidade, acompanhamento e avaliação anterior não pontuam; dado ausente não vira zero; IAL não é CRPS; não há suspensão automática.

## Testes

Consulte a saída de `pytest` entregue com o pacote e a suíte em `tests/`.

## Implantação

Ver README e `docs/implantacao.md`.


## Resultado de testes nesta entrega

- `python -m compileall`: aprovado.
- `pytest`: **18 testes aprovados**, 0 falhas; 2 avisos de depreciação do `datetime.utcnow()` no SQLAlchemy/Python 3.13.
- Inicialização SQLite: aprovada.
- Carga de 30 estudantes sintéticos: aprovada.
- Exportação da Planilha Unificada: aprovada.
- Dockerfile foi gerado; o build Docker não foi executado neste ambiente por indisponibilidade do daemon Docker.
