# Avaliação de Rendimento e Acompanhamento das Trajetórias Estudantis – PAE/UFPR

Aplicação Streamlit/Python para apoiar o processamento acadêmico e a jornada profissional da Avaliação de Rendimento do PAE/UFPR.

## Princípio institucional

A aplicação **não decide suspensão automaticamente**. Mantém separados MCN, IAL, fatores de proteção, acompanhamento, MAIC, MNA, PIAAP, CRPS e decisão administrativa.

## Arquitetura

Fontes institucionais → ingestão/validação → SQLite (MVP) → serviços/domínio → Streamlit → exportações Excel.

A persistência usa SQLAlchemy e está preparada para migração futura para PostgreSQL via `DATABASE_URL`.

## Instalação local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/load_sample_data.py
streamlit run app.py
```

No modo demo: usuário `admin`, senha `admin`. Troque/desative antes de qualquer uso real.

## Docker

```bash
docker compose up --build
```

## Migrations

```bash
alembic upgrade head
```

## Dados sintéticos

`scripts/load_sample_data.py` cria 30 estudantes fictícios. Nenhum dado real integra o repositório.

## MCN

`src/domain/mcn/rules.py` implementa os arts. 17–21 separadamente, sem score global. Dados insuficientes geram estados como `DADO_PENDENTE`, `PARAMETRO_NAO_CONFIRMADO`, `REQUER_CONFERENCIA` ou `NAO_CALCULAVEL`.

## IAL

A configuração inicial de teste usa 40% rendimento, 35% frequência e 25% progressão. Pesos e faixas estão em `configs/ial.yaml` e devem ser validados empiricamente antes da adoção institucional definitiva.

## Priorização

A seleção usa camadas explicáveis e parâmetro `N`; não corresponde aos maiores IAL. A lista final exige validação da equipe e alterações manuais justificadas.

## Fatores de proteção

Quatro fontes: SIGA; P4E/PROAFE/CATRIM; formulário; atendimento. Não recebem score e não aumentam IAL ou CRPS.

## Jornada profissional

A aplicação possui páginas para contextualização, atendimento, MAIC, MNA, PIAAP, manutenção, monitoramento, reavaliação, CRPS, recursos e Comissão.

## Segurança/LGPD

O modo demo é apenas para desenvolvimento. Produção exige autenticação institucional, revisão de perfis, política de retenção, backup seguro, secrets e infraestrutura persistente. Dados sensíveis devem ser minimizados nos painéis e no módulo da Comissão.

## Testes

```bash
pytest
```

## Exportação

A página Administração exporta a Planilha Unificada com 19 abas (`00_CONTROLE` a `18_DICIONARIO_DADOS`).

## PostgreSQL

Configure `DATABASE_URL` para PostgreSQL e instale o driver correspondente. As regras de domínio não precisam mudar.

## Streamlit Community Cloud

SQLite local pode ser efêmero em hospedagem cloud. Para uso real multiusuário, prefira banco externo persistente, idealmente PostgreSQL.

## Documentação

Consulte `docs/` e `IMPLEMENTATION_REPORT.md`.
