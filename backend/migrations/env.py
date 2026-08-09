# -*- coding: utf-8 -*-
"""Alembic 环境：从 DATABASE_URL（环境变量优先）读取数据库 URL，目标元数据为全部模型。"""
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app import models  # noqa: E402,F401  确保模型注册到 Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _prepare_sqlite_path(url: str) -> None:
    if url.startswith("sqlite:///"):
        path = url.removeprefix("sqlite:///")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)


def run_migrations_offline() -> None:
    url = os.environ.get("DATABASE_URL", "").strip() or settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    database_url = os.environ.get("DATABASE_URL", "").strip() or settings.database_url
    _prepare_sqlite_path(database_url)
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
