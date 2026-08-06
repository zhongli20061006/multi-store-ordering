from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from app.models import Order
from tests.conftest import login

CN_OFFSET = timedelta(hours=8)


def _create(client, seed, key, item_id=None, phone="13900000001"):
    return client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "看板测试",
            "customer_phone": phone,
            "idempotency_key": key,
            "items": [{"menu_item_id": item_id or seed["item1_id"], "quantity": 1}],
        },
    ).json()["data"]


def _backdate(db_session_factory, order_id, local_dt):
    utc_naive = (local_dt - CN_OFFSET).replace(tzinfo=None)
    db = db_session_factory()
    db.execute(update(Order).where(Order.id == order_id).values(created_at=utc_naive))
    db.commit()
    db.close()


def _set_status(db_session_factory, order_id, status):
    db = db_session_factory()
    db.execute(update(Order).where(Order.id == order_id).values(order_status=status))
    db.commit()
    db.close()


def _local_today():
    return (datetime.now(timezone.utc) + CN_OFFSET).date()


def test_dashboard_requires_login_and_store_access(client, seed):
    assert client.get(f"/api/v1/admin/stores/{seed['store1_id']}/dashboard").status_code == 401
    other = login(client, "admin2")
    assert client.get(f"/api/v1/admin/stores/{seed['store1_id']}/dashboard", headers=other).status_code == 403


def test_dashboard_daily_and_today(client, seed, db_session_factory):
    today = _local_today()
    yesterday = today - timedelta(days=1)
    old = today - timedelta(days=8)

    a = _create(client, seed, "dash-a-001", item_id=seed["item2_id"])  # 1800 completed 今日
    b = _create(client, seed, "dash-b-001")  # 1200 pending 今日
    c = _create(client, seed, "dash-c-001")  # 1200 completed 昨日
    d = _create(client, seed, "dash-d-001")  # 1200 completed 8天前（不计）
    e = _create(client, seed, "dash-e-001")  # 1200 cancelled 今日（不计）

    _set_status(db_session_factory, a["id"], "completed")
    _set_status(db_session_factory, c["id"], "completed")
    _set_status(db_session_factory, d["id"], "completed")
    _set_status(db_session_factory, e["id"], "cancelled")

    _backdate(db_session_factory, a["id"], datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + CN_OFFSET)
    _backdate(db_session_factory, b["id"], datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + CN_OFFSET)
    _backdate(db_session_factory, c["id"], datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc) + CN_OFFSET)
    _backdate(db_session_factory, d["id"], datetime.combine(old, datetime.min.time(), tzinfo=timezone.utc) + CN_OFFSET)
    _backdate(db_session_factory, e["id"], datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + CN_OFFSET)

    headers = login(client, "admin1")
    data = client.get(f"/api/v1/admin/stores/{seed['store1_id']}/dashboard", headers=headers).json()["data"]

    assert len(data["daily"]) == 7
    by_date = {row["date"]: row for row in data["daily"]}
    assert by_date[today.strftime("%m-%d")]["order_count"] == 2
    assert by_date[today.strftime("%m-%d")]["revenue_cents"] == 1800
    assert by_date[yesterday.strftime("%m-%d")]["order_count"] == 1
    assert by_date[yesterday.strftime("%m-%d")]["revenue_cents"] == 1200
    assert by_date[(today - timedelta(days=6)).strftime("%m-%d")]["order_count"] == 0

    today_stats = data["today"]
    assert today_stats["order_count"] == 2
    assert today_stats["pending"] == 1
    assert today_stats["completed"] == 1
    assert today_stats["revenue_cents"] == 1800
