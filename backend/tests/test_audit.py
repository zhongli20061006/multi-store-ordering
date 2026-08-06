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
