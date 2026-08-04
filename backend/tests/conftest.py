import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.deps import get_db
from app.core.database import Base
from app.core.security import hash_password
from app.main import app
from app.models import MenuCategory, MenuItem, Store, StoreAdmin, User


@pytest.fixture()
def db_session_factory(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed(db_session_factory):
    db = db_session_factory()
    admin1 = User(username="admin1", password_hash=hash_password("admin123456"), display_name="中山店长")
    admin2 = User(username="admin2", password_hash=hash_password("admin123456"), display_name="万达店长")
    db.add_all([admin1, admin2])
    db.flush()

    store1 = Store(name="中山路店", address="中山路1号", phone="13800000001", sort_order=1)
    store2 = Store(name="万达店", address="万达B1", phone="13800000002", sort_order=2)
    db.add_all([store1, store2])
    db.flush()

    db.add_all(
        [
            StoreAdmin(store_id=store1.id, user_id=admin1.id),
            StoreAdmin(store_id=store2.id, user_id=admin2.id),
        ]
    )

    cat1 = MenuCategory(store_id=store1.id, name="招牌饮品", sort_order=1)
    cat2 = MenuCategory(store_id=store2.id, name="招牌饮品", sort_order=1)
    db.add_all([cat1, cat2])
    db.flush()

    item1 = MenuItem(store_id=store1.id, category_id=cat1.id, name="招牌奶茶", price_cents=1200, sort_order=1)
    item2 = MenuItem(store_id=store1.id, category_id=cat1.id, name="限量奶昔", price_cents=1800, stock=1, sort_order=2)
    item3 = MenuItem(store_id=store2.id, category_id=cat2.id, name="招牌奶茶", price_cents=1300, sort_order=1)
    db.add_all([item1, item2, item3])
    db.commit()

    result = {
        "admin1_id": admin1.id,
        "admin2_id": admin2.id,
        "store1_id": store1.id,
        "store2_id": store2.id,
        "cat1_id": cat1.id,
        "cat2_id": cat2.id,
        "item1_id": item1.id,
        "item2_id": item2.id,
        "item3_id": item3.id,
    }
    db.close()
    return result


def login(client, username: str, password: str = "admin123456") -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}
