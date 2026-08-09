from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def utcnow() -> datetime:
    """统一时间源：UTC 纳秒级时间戳，落库为无时区标记的 UTC。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


def _prepare_sqlite_path(url: str) -> None:
    """sqlite 文件不存在时确保目录存在。"""
    if url.startswith("sqlite:///"):
        path = url.removeprefix("sqlite:///")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)


def create_db_engine(database_url: str):
    _prepare_sqlite_path(database_url)
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            pool_size=1,
            max_overflow=0,
        )

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

        return engine
    return create_engine(database_url)


engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """按 Alembic 迁移建库/升级（幂等，替代 create_all + 幂等加列）。

    全新空库由 0001 基线建全表；存量演示库由基线迁移收敛（跳过已有表、
    补历史缺失列），后续 schema 变更走增量迁移。
    """
    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    command.upgrade(cfg, "head")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
