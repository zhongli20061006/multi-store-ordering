from app.core.database import create_db_engine


def test_sqlite_engine_enables_wal_and_busy_timeout(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'cfg.db'}")
    with engine.connect() as conn:
        journal = conn.exec_driver_sql("PRAGMA journal_mode").scalar_one()
        timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar_one()
    assert journal == "wal"
    assert timeout == 5000
    engine.dispose()


def test_ensure_additive_columns_adds_coordinates(tmp_path):
    from sqlalchemy import inspect

    from app.core.db_migrate import ensure_additive_columns

    engine = create_db_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE stores (id INTEGER PRIMARY KEY, name VARCHAR(80), address VARCHAR(200), phone VARCHAR(20))"
        )
        conn.exec_driver_sql(
            "CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER, item_name VARCHAR(80))"
        )
        conn.exec_driver_sql(
            "CREATE TABLE menu_items (id INTEGER PRIMARY KEY, store_id INTEGER, name VARCHAR(60), price_cents INTEGER)"
        )
    ensure_additive_columns(engine)
    store_cols = {c["name"] for c in inspect(engine).get_columns("stores")}
    item_cols = {c["name"] for c in inspect(engine).get_columns("order_items")}
    menu_cols = {c["name"] for c in inspect(engine).get_columns("menu_items")}
    assert {"latitude", "longitude"} <= store_cols
    assert "specs" in item_cols
    assert "spec_groups" in menu_cols
    engine.dispose()
