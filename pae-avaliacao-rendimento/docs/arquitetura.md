# Arquitetura

Quatro camadas: interface Streamlit, serviços, domínio e repositórios/persistência. Regras normativas e fórmulas não ficam nas páginas. SQLite é o banco do MVP; SQLAlchemy desacopla a persistência e permite futura migração para PostgreSQL.
