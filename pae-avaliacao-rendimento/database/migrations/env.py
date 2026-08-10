from alembic import context
from sqlalchemy import engine_from_config,pool
from src.db.base import Base
import src.models.models
config=context.config;target_metadata=Base.metadata
def offline():
    context.configure(url=config.get_main_option('sqlalchemy.url'),target_metadata=target_metadata,literal_binds=True)
    with context.begin_transaction():context.run_migrations()
def online():
    e=engine_from_config(config.get_section(config.config_ini_section),prefix='sqlalchemy.',poolclass=pool.NullPool)
    with e.connect() as c:
        context.configure(connection=c,target_metadata=target_metadata)
        with context.begin_transaction():context.run_migrations()
offline() if context.is_offline_mode() else online()
