from app.core.database import create_db_engine


def test_sqlite_engine_enables_wal_and_busy_timeout(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'cfg.db'}")
    with engine.connect() as conn:
        journal = conn.exec_driver_sql("PRAGMA journal_mode").scalar_one()
        timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar_one()
    assert journal == "wal"
    assert timeout == 5000
    engine.dispose()
