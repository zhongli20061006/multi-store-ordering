from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
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
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """原型期：按模型建表（幂等）。正式迁移见 database-design.md。"""
    from app import models  # noqa: F401  确保模型已注册

    Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
