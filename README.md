# Avaliação de Rendimento e Acompanhamento das Trajetórias Estudantis – PAE/UFPR

**Versão 0.4.1 – primeira versão preparada para produção com deploy Streamlit.**

Aplicação Python/Streamlit para apoiar toda a jornada da Avaliação de Rendimento PAE/UFPR, desde a importação das bases até acompanhamento, reavaliação e garantias processuais.

## Princípios

A aplicação mantém separados **MCN, IAL, fatores de proteção, acompanhamento, MAIC, MNA, PIAAP, CRPS e decisão administrativa**. Não existe suspensão automática, score de vulnerabilidade, score de acompanhamento ou conversão automática de IAL em CRPS.

## Stack

Python 3.11, Streamlit, Pandas, SQLAlchemy, SQLite/PostgreSQL, Alembic, Plotly, OpenPyXL/XlsxWriter, Pandera e pytest.

## Instalação local

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate      # Windows
pip install -r requirements.txt
python scripts/init_db.py
python scripts/load_sample_data.py
streamlit run app.py
```

No ambiente de desenvolvimento, se `APP_DEMO_MODE=true`, o login demo permanece `admin/admin`. **Esse login é bloqueado quando `APP_ENV=production`.**

## Produção no Streamlit

1. copie `.streamlit/secrets.toml.example` apenas como referência;
2. configure secrets diretamente no ambiente de deploy;
3. defina `app.env="production"` e `app.demo_mode=false`;
4. configure `database.url`;
5. gere hashes PBKDF2 com `python scripts/hash_password.py "senha"`;
6. cadastre usuários no secret ou no banco;
7. após subir a aplicação, abra **Produção e Prontidão**.

Consulte `docs/deploy_streamlit_producao.md`.

## Banco

Desenvolvimento/homologação: SQLite.

Produção multiusuária: a mesma aplicação aceita PostgreSQL por `DATABASE_URL` ou `[database].url` nos Streamlit Secrets. A camada SQLAlchemy evita acoplamento das regras de MCN/IAL ao banco.

## Importação real

A página **Bases, Importação e Processamento do Ciclo** aceita as bases formais do Projeto Técnico e possui compatibilidade com a `PLANILHA COMPLETA` utilizada na Calculadora ITA 2025. Os dados legados alimentam o modelo atual apenas quando a evidência é tecnicamente suficiente; lacunas permanecem como pendência/conferência.

## Processamento

O pipeline produz: universo → MCN → IAL → fatores prévios → acompanhamentos → histórico → priorização N → validação humana → distribuição → ficha pré-análise.

## Jornada profissional

A aplicação contém contextualização, atendimento/escuta, MAIC, MNA, PIAAP, manutenção, monitoramento, reavaliação, CRPS, recursos e Comissão Paritária. A ficha individual mostra a próxima ação calculada pelo workflow.

## Novidades 0.4

- autenticação PBKDF2;
- RBAC por página;
- sessão com expiração;
- secrets de produção;
- PostgreSQL opcional;
- checklist de prontidão;
- backups;
- retenção de logs;
- sensibilidade do IAL;
- auditoria de equidade;
- rascunhos de comunicação sem envio automático;
- CI GitHub;
- configuração Streamlit endurecida;
- workflow integrado de reavaliação/CRPS/recurso.

## Testes

```bash
pytest -q
```

Também execute:

```bash
python -m compileall -q .
python scripts/validate_environment.py
```

## Docker

```bash
docker compose up --build
```

## Dados sintéticos

`scripts/load_sample_data.py` cria dados fictícios. Nenhum dado real integra o repositório.

## Exportação

A aplicação exporta a Planilha Unificada com 19 abas. A página Produção e Prontidão também gera backup institucional.

## Estrutura documental

- `docs/refatoracao_0_3.md` – integração com o modelo ITA 2025;
- `docs/refatoracao_0_4.md` – segurança/homologação/produção;
- `docs/deploy_streamlit_producao.md` – implantação;
- `docs/seguranca_lgpd.md` – controles;
- `docs/requisitos_implementados.md` – cobertura;
- `IMPLEMENTATION_REPORT.md` – situação técnica da entrega.

## Pendências externas, não bugs de implementação

Alguns pontos continuam dependentes de decisão/insumo institucional: inventário definitivo do art. 18, cálculo final de tempo computável do art. 21, fonte final da taxa de turma do art. 20, pactuação definitiva dos pesos/faixas do IAL, política institucional de retenção e eventual integração de identidade/SSO.

## Alterações da versão 0.4.2 — inicialização automática no Streamlit

A aplicação agora executa automaticamente, no startup:

1. criação/verificação do schema do banco;
2. teste de conexão;
3. criação idempotente dos ciclos definidos em `configs/ciclos.yaml` (por padrão 2025/2 e 2026/1).

Portanto, **não é necessário executar `scripts/init_db.py` nem `scripts/load_sample_data.py` para iniciar a versão de produção**. O script de dados sintéticos continua existindo apenas para testes/homologação.

O perfil `ADMIN` possui, em **Administração e Configuração → Ciclos**, funções para:

- criar novo ciclo;
- ativar ciclo;
- encerrar ciclo;
- reabrir ciclo.

### Persistência no Streamlit

Para deploy real no Streamlit, configure um PostgreSQL externo persistente nos Secrets:

```toml
[app]
env = "production"
demo_mode = false

[database]
url = "postgresql+psycopg://USUARIO:SENHA@HOST:5432/BANCO?sslmode=require"
```

SQLite continua suportado para desenvolvimento e homologação temporária, mas a página **Produção e Prontidão** considera SQLite local inadequado para produção no Streamlit por não oferecer garantia de persistência após reinícios/redeploys em ambientes efêmeros.
