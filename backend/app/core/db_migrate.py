# -*- coding: utf-8 -*-
"""原型期幂等加列迁移：新表由 create_all 建全；存量演示库仅补加列，不删不改。"""
from sqlalchemy import inspect, text


def ensure_additive_columns(engine) -> None:
    inspector = inspect(engine)
    store_cols = {c["name"] for c in inspector.get_columns("stores")}
    item_cols = {c["name"] for c in inspector.get_columns("order_items")}
    menu_cols = {c["name"] for c in inspector.get_columns("menu_items")}
    with engine.begin() as conn:
        if "open_time" not in store_cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN open_time VARCHAR(5)"))
        if "close_time" not in store_cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN close_time VARCHAR(5)"))
        if "latitude" not in store_cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN latitude REAL"))
        if "longitude" not in store_cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN longitude REAL"))
        if "image_url" not in store_cols:
            conn.execute(text("ALTER TABLE stores ADD COLUMN image_url TEXT"))
        if "spec_groups" not in menu_cols:
            conn.execute(text("ALTER TABLE menu_items ADD COLUMN spec_groups TEXT"))
        if "specs" not in item_cols:
            conn.execute(text("ALTER TABLE order_items ADD COLUMN specs TEXT"))
        if "category_name" not in item_cols:
            conn.execute(text("ALTER TABLE order_items ADD COLUMN category_name VARCHAR(40)"))
