from app.core.database import create_db_engine


def test_sqlite_engine_enables_wal_and_busy_timeout(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'cfg.db'}")
    with engine.connect() as conn:
        journal = conn.exec_driver_sql("PRAGMA journal_mode").scalar_one()
        timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar_one()
    assert journal == "wal"
    assert timeout == 5000
    engine.dispose()


def _run_migrations(db_path):
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    command.upgrade(cfg, "head")


def test_baseline_migration_creates_full_schema_on_fresh_db(tmp_path, monkeypatch):
    from sqlalchemy import inspect

    db_path = tmp_path / "fresh.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    _run_migrations(db_path)

    engine = create_db_engine(f"sqlite:///{db_path}")
    tables = set(inspect(engine).get_table_names())
    assert {
        "users",
        "stores",
        "store_admins",
        "menu_categories",
        "menu_items",
        "orders",
        "order_items",
        "store_banners",
        "audit_logs",
        "alembic_version",
    } <= tables
    engine.dispose()


def test_baseline_migration_converges_legacy_db(tmp_path, monkeypatch):
    from sqlalchemy import inspect

    db_path = tmp_path / "legacy.db"
    engine = create_db_engine(f"sqlite:///{db_path}")
    # 模拟 ensure_additive_columns 时代的存量库：仅缺历史补列
    # （stores 营业时间/经纬度/封面/主题；menu_items.spec_groups；order_items.specs/category_name）
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE stores ("
            "id INTEGER PRIMARY KEY, name VARCHAR(80), address VARCHAR(200), phone VARCHAR(20), "
            "status VARCHAR(16), sort_order INTEGER, created_at DATETIME, updated_at DATETIME)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE order_items ("
            "id INTEGER PRIMARY KEY, order_id INTEGER, menu_item_id INTEGER, item_name VARCHAR(60), "
            "unit_price_cents INTEGER, quantity INTEGER, subtotal_cents INTEGER)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE menu_items ("
            "id INTEGER PRIMARY KEY, store_id INTEGER, category_id INTEGER, name VARCHAR(60), "
            "description VARCHAR(200), price_cents INTEGER, stock INTEGER, image_url VARCHAR(500), "
            "is_active BOOLEAN, sort_order INTEGER, created_at DATETIME, updated_at DATETIME)"
        )
    engine.dispose()

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    _run_migrations(db_path)

    engine = create_db_engine(f"sqlite:///{db_path}")
    tables = set(inspect(engine).get_table_names())
    assert {"stores", "order_items", "menu_items", "users", "orders", "alembic_version"} <= tables
    store_cols = {c["name"] for c in inspect(engine).get_columns("stores")}
    item_cols = {c["name"] for c in inspect(engine).get_columns("order_items")}
    menu_cols = {c["name"] for c in inspect(engine).get_columns("menu_items")}
    assert {"latitude", "longitude", "open_time", "close_time", "theme", "image_url", "status"} <= store_cols
    assert {"specs", "category_name"} <= item_cols
    assert "spec_groups" in menu_cols
    engine.dispose()
