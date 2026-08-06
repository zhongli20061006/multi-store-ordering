# -*- coding: utf-8 -*-
"""原型期幂等加列迁移：新表由 create_all 建全；存量演示库仅补加列，不删不改。"""
from sqlalchemy import inspect, text


def ensure_additive_columns(engine) -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("stores")}
    with engine.begin() as conn:
        if "open_time" not in cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN open_time VARCHAR(5)"))
        if "close_time" not in cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN close_time VARCHAR(5)"))
