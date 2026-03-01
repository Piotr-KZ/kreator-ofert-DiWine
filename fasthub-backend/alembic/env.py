"""
Alembic environment configuration for PostgreSQL
Uses fasthub_core migration helper for unified model registry.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import from fasthub_core — single source of truth
from fasthub_core.config import get_settings
from fasthub_core.db.migrations import get_metadata, get_sync_database_url

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy URL — lazy load settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", get_sync_database_url(settings.DATABASE_URL))

# All fasthub_core models registered via get_metadata()
target_metadata = get_metadata()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode"""

    configuration = config.get_section(config.config_ini_section)
    settings = get_settings()
    configuration["sqlalchemy.url"] = get_sync_database_url(settings.DATABASE_URL)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
