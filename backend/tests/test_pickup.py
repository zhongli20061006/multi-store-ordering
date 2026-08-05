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


def _accept(client, seed, order):
    headers = login(client, "admin1")
    resp = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    assert resp.status_code == 200


def _serve(client, seed, order):
    _accept(client, seed, order)
    headers = login(client, "admin1")
    resp = client.patch(
        f"/api/v1/admin/orders/{order['id']}/status",
        json={"order_status": "served"},
        headers=headers,
    )
    assert resp.status_code == 200


def test_customer_pickup_served_completes(client, seed):
    order = _create(client, seed, "pickup-001")
    _serve(client, seed, order)
    resp = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    assert resp.status_code == 200
    assert resp.json()["data"]["order_status"] == "completed"


def test_customer_pickup_twice_idempotent(client, seed):
    order = _create(client, seed, "pickup-002")
    _serve(client, seed, order)
    first = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    second = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    assert first.status_code == 200 and second.status_code == 200
    assert second.json()["data"]["order_status"] == "completed"


def test_customer_pickup_accepted_rejected(client, seed):
    order = _create(client, seed, "pickup-003")
    _accept(client, seed, order)
    resp = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    assert resp.status_code == 409


def test_customer_pickup_pending_rejected(client, seed):
    order = _create(client, seed, "pickup-004")
    resp = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    assert resp.status_code == 409


def test_customer_pickup_cancelled_rejected(client, seed):
    order = _create(client, seed, "pickup-005")
    headers = login(client, "admin1")
    client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    resp = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000001"})
    assert resp.status_code == 409


def test_customer_pickup_wrong_phone_not_found(client, seed):
    order = _create(client, seed, "pickup-006")
    _serve(client, seed, order)
    resp = client.post(f"/api/v1/orders/{order['order_no']}/pickup", json={"phone": "13900000002"})
    assert resp.status_code == 404
