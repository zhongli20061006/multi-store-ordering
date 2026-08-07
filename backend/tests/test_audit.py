import csv
import io
from datetime import datetime

from tests.conftest import login


def _create_order(client, seed, key):
    resp = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": key,
            "items": [{"menu_item_id": seed["item1_id"], "quantity": 1}],
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]


def _audit(client, order_id, headers):
    resp = client.get(f"/api/v1/admin/orders/{order_id}/audit", headers=headers)
    assert resp.status_code == 200
    return resp.json()["data"]


def test_merchant_actions_write_audit(client, seed):
    order = _create_order(client, seed, "audit-merchant-001")
    headers = login(client, "admin1")
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "served"},
        headers=headers,
    )
    client.patch(f"/api/v1/admin/orders/{order['id']}/payment", json={"payment_status": "paid"}, headers=headers)
    logs = _audit(client, order["id"], headers)
    assert [log["action"] for log in logs] == ["accepted", "served", "paid"]
    assert all(log["actor_type"] == "merchant" for log in logs)
    assert all(log["actor_id"] == seed["admin1_id"] for log in logs)


def test_merchant_cancel_writes_audit_with_reason(client, seed):
    order = _create_order(client, seed, "audit-cancel-001")
    headers = login(client, "admin1")
    client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_made"},
        headers=headers,
    )
    logs = _audit(client, order["id"], headers)
    assert logs[0]["action"] == "cancelled"
    assert logs[0]["detail"] == {"cancel_reason": "merchant_cancel_made", "prev_status": "pending"}


def test_customer_cancel_and_pickup_write_audit(client, seed):
    order = _create_order(client, seed, "audit-customer-001")
    resp = client.post(f"/api/v1/orders/{order['order_no']}/cancel", json={"phone": "13900000001"})
    assert resp.status_code == 200
    headers = login(client, "admin1")
    logs = _audit(client, order["id"], headers)
    assert logs[0]["action"] == "customer_cancelled"
    assert logs[0]["actor_type"] == "customer"
    assert logs[0]["actor_id"] is None

    order2 = _create_order(client, seed, "audit-customer-002")
    client.patch(
        f"/api/v1/admin/orders/{order2['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    client.patch(
        f"/api/v1/admin/orders/{order2['id']}/status",
        json={"order_status": "served"},
        headers=headers,
    )
    client.post(f"/api/v1/orders/{order2['order_no']}/pickup", json={"phone": "13900000001"})
    logs2 = _audit(client, order2["id"], headers)
    assert logs2[-1]["action"] == "customer_pickup"
    assert logs2[-1]["actor_type"] == "customer"


def test_audit_requires_login_and_store_access(client, seed):
    order = _create_order(client, seed, "audit-scope-001")
    anon = client.get(f"/api/v1/admin/orders/{order['id']}/audit")
    assert anon.status_code == 401
    other = login(client, "admin2")
    blocked = client.get(f"/api/v1/admin/orders/{order['id']}/audit", headers=other)
    assert blocked.status_code == 403


def _accept(client, order, headers):
    resp = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    assert resp.status_code == 200


def test_admin_audit_logs_scoped_to_user_stores(client, seed):
    order1 = _create_order(client, seed, "logs-scope-001")
    h1 = login(client, "admin1")
    _accept(client, order1, h1)
    order2 = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store2_id"],
            "customer_name": "万达顾客",
            "customer_phone": "13900000002",
            "idempotency_key": "logs-scope-002",
            "items": [{"menu_item_id": seed["item3_id"], "quantity": 1}],
        },
    ).json()["data"]
    h2 = login(client, "admin2")
    _accept(client, order2, h2)
    mine = client.get("/api/v1/admin/audit-logs", headers=h1).json()["data"]
    assert mine["total"] == 1
    assert mine["items"][0]["order_no"] == order1["order_no"]
    assert mine["items"][0]["store_name"] == "中山路店"
    cross = client.get(
        "/api/v1/admin/audit-logs",
        params={"store_id": seed["store2_id"]},
        headers=h1,
    )
    assert cross.status_code == 403
    anon = client.get("/api/v1/admin/audit-logs")
    assert anon.status_code == 401


def test_admin_audit_logs_date_filter_and_pagination(client, seed, db_session_factory):
    from app.models import AuditLog
    from sqlalchemy import update

    orders = [_create_order(client, seed, f"logs-page-00{i}") for i in range(3)]
    headers = login(client, "admin1")
    for order in orders:
        _accept(client, order, headers)
    db = db_session_factory()
    db.execute(
        update(AuditLog)
        .where(AuditLog.order_id == orders[0]["id"])
        .values(created_at=datetime(2026, 8, 4, 16, 0, 0))
    )
    db.commit()
    db.close()
    page1 = client.get(
        "/api/v1/admin/audit-logs",
        params={"page": 1, "page_size": 2},
        headers=headers,
    ).json()["data"]
    assert page1["total"] == 3
    assert len(page1["items"]) == 2
    day = client.get(
        "/api/v1/admin/audit-logs",
        params={"date_from": "2026-08-05", "date_to": "2026-08-05"},
        headers=headers,
    ).json()["data"]
    assert day["total"] == 1


def _audit_export_rows(resp):
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    text = resp.content.decode("utf-8")
    assert text.startswith("\ufeff")
    return [r for r in csv.reader(io.StringIO(text.lstrip("\ufeff"))) if r]


def test_admin_audit_logs_export(client, seed):
    order = _create_order(client, seed, "logs-exp-001")
    headers = login(client, "admin1")
    _accept(client, order, headers)
    rows = _audit_export_rows(client.get("/api/v1/admin/audit-logs/export", headers=headers))
    assert rows[0] == ["时间", "订单号", "门店", "动作", "操作方", "详情", "操作人ID"]
    body = rows[1]
    assert body[1] == order["order_no"]
    assert body[3] == "接单"
    assert body[4] == "商家"


def test_admin_audit_logs_export_respects_store_access(client, seed):
    order = _create_order(client, seed, "logs-exp-002")
    headers = login(client, "admin1")
    _accept(client, order, headers)
    other = login(client, "admin2")
    blocked = client.get(
        "/api/v1/admin/audit-logs/export",
        params={"store_id": seed["store1_id"]},
        headers=other,
    )
    assert blocked.status_code == 403
