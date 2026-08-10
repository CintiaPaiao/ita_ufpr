# Deploy da primeira versão de produção no Streamlit

## 1. Banco

A aplicação lê `DATABASE_URL` de variável de ambiente ou de `.streamlit/secrets.toml`.

Para desenvolvimento:

```toml
[database]
url = "sqlite:///database/pae.db"
```

Para implantação institucional multiusuária, configure um PostgreSQL persistente e forneça a URL pelo secret `database.url`.

## 2. Autenticação

Em produção:

```toml
[app]
env = "production"
demo_mode = false
```

Crie hashes com:

```bash
python scripts/hash_password.py "SUA_SENHA_FORTE"
```

E configure usuários no secrets:

```toml
[[auth.users]]
username = "usuario"
display_name = "Nome"
role = "PROFISSIONAL"
password_hash = "pbkdf2_sha256$..."
```

Perfis disponíveis: `ADMIN`, `PROFISSIONAL`, `CHEFIA`, `COMISSAO`, `AUDITOR`.

## 3. Secrets

Nunca versione `.streamlit/secrets.toml`. O repositório contém somente `secrets.toml.example`.

## 4. Checklist

Após o deploy, acesse **Produção e Prontidão**. Não utilizar base real enquanto houver falha classificada como crítica.

## 5. Primeiro ciclo

1. importar bases;
2. conferir inconsistências;
3. processar MCN/IAL/priorização;
4. validar seleção;
5. distribuir casos;
6. seguir fila/ficha profissional;
7. registrar manutenção/monitoramento;
8. congelar/arquivar conforme procedimento institucional.

## 6. Backup

A página Produção e Prontidão gera ZIP institucional contendo Planilha Unificada e, quando SQLite, snapshot consistente do banco. O arquivo deve permanecer em armazenamento institucional restrito.
