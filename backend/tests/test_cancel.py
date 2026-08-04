from tests.conftest import login


def _create(client, seed, key):
    return client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": key,
            "items": [{"menu_item_id": seed["item2_id"], "quantity": 1}],
        },
    ).json()["data"]


def _stock_of(client, store_id, item_id):
    menu = client.get(f"/api/v1/stores/{store_id}/menu").json()["data"]
    return next(i for g in menu for i in g["items"] if i["id"] == item_id)["stock"]


def test_customer_cancel_pending_restocks(client, seed):
    order = _create(client, seed, "cancel-c-001")
    resp = client.post(f"/api/v1/orders/{order['order_no']}/cancel", json={"phone": "13900000001"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["order_status"] == "cancelled"
    assert data["cancel_reason"] == "customer_cancel"
    assert _stock_of(client, seed["store1_id"], seed["item2_id"]) == 1


def test_customer_cancel_rejected_after_accepted(client, seed):
    order = _create(client, seed, "cancel-c-002")
    headers = login(client, "admin1")
    client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    resp = client.post(f"/api/v1/orders/{order['order_no']}/cancel", json={"phone": "13900000001"})
    assert resp.status_code == 409


def test_customer_cancel_wrong_phone_not_found(client, seed):
    order = _create(client, seed, "cancel-c-003")
    resp = client.post(f"/api/v1/orders/{order['order_no']}/cancel", json={"phone": "13900000002"})
    assert resp.status_code == 404


def test_merchant_cancel_not_made_restocks(client, seed):
    order = _create(client, seed, "cancel-m-001")
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert _stock_of(client, seed["store1_id"], seed["item2_id"]) == 1


def test_merchant_cancel_made_does_not_restock(client, seed):
    order = _create(client, seed, "cancel-m-002")
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_made"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert _stock_of(client, seed["store1_id"], seed["item2_id"]) == 0


def test_double_cancel_is_idempotent(client, seed):
    order = _create(client, seed, "cancel-m-003")
    headers = login(client, "admin1")
    first = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    second = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert first.status_code == 200 and second.status_code == 200
    assert _stock_of(client, seed["store1_id"], seed["item2_id"]) == 1


def test_admin_cancel_cross_store_blocked(client, seed):
    order = _create(client, seed, "cancel-m-004")
    headers = login(client, "admin2")
    resp = client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert resp.status_code == 403
