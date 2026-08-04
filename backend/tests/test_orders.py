from tests.conftest import login
from sqlalchemy import inspect


def _order_payload(seed, **overrides):
    payload = {
        "store_id": seed["store1_id"],
        "customer_name": "测试顾客",
        "customer_phone": "13900000001",
        "idempotency_key": "test-order-key-0001",
        "items": [{"menu_item_id": seed["item1_id"], "quantity": 2}],
    }
    payload.update(overrides)
    return payload


def test_create_order_computes_total_from_db(client, seed):
    resp = client.post("/api/v1/orders", json=_order_payload(seed))
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total_cents"] == 2400
    assert data["item_count"] == 2
    assert data["order_status"] == "pending"
    assert data["payment_status"] == "unpaid"
    assert data["entry_type"] == "preorder"


def test_dinein_entry_accepted(client, seed):
    resp = client.post("/api/v1/orders", json=_order_payload(seed, entry_type="dinein", idempotency_key="dinein-key-0001"))
    assert resp.status_code == 201
    assert resp.json()["data"]["entry_type"] == "dinein"


def test_duplicate_item_in_one_order_rejected(client, seed):
    payload = _order_payload(
        seed,
        idempotency_key="dup-item-key-001",
        items=[{"menu_item_id": seed["item1_id"], "quantity": 1}, {"menu_item_id": seed["item1_id"], "quantity": 1}],
    )
    resp = client.post("/api/v1/orders", json=payload)
    assert resp.status_code == 400


def test_unknown_item_rejected(client, seed):
    payload = _order_payload(seed, idempotency_key="unknown-key-001", items=[{"menu_item_id": 99999, "quantity": 1}])
    resp = client.post("/api/v1/orders", json=payload)
    assert resp.status_code == 400


def test_inactive_item_rejected(client, seed):
    headers = login(client, "admin1")
    client.delete(f"/api/v1/admin/stores/{seed['store1_id']}/items/{seed['item2_id']}", headers=headers)
    payload = _order_payload(seed, idempotency_key="inactive-key-001", items=[{"menu_item_id": seed["item2_id"], "quantity": 1}])
    resp = client.post("/api/v1/orders", json=payload)
    assert resp.status_code == 400


def test_closed_store_rejected(client, seed):
    headers = login(client, "admin1")
    client.patch(f"/api/v1/admin/stores/{seed['store1_id']}/status", json={"status": "closed"}, headers=headers)
    resp = client.post("/api/v1/orders", json=_order_payload(seed, idempotency_key="closed-key-001"))
    assert resp.status_code == 409


def test_idempotent_replay_returns_same_order(client, seed):
    payload = _order_payload(seed)
    first = client.post("/api/v1/orders", json=payload)
    second = client.post("/api/v1/orders", json=payload)
    assert first.status_code == 201 and second.status_code == 201
    assert first.json()["data"]["order_no"] == second.json()["data"]["order_no"]
    order_no = first.json()["data"]["order_no"]
    mine = client.get("/api/v1/orders", params={"phone": "13900000001", "order_no": order_no}).json()["data"]
    assert mine["order_no"] == order_no


def test_limited_stock_prevents_oversell(client, seed):
    first = client.post(
        "/api/v1/orders",
        json=_order_payload(seed, idempotency_key="stock-key-001", items=[{"menu_item_id": seed["item2_id"], "quantity": 1}]),
    )
    assert first.status_code == 201
    second = client.post(
        "/api/v1/orders",
        json=_order_payload(seed, idempotency_key="stock-key-002", items=[{"menu_item_id": seed["item2_id"], "quantity": 1}]),
    )
    assert second.status_code == 409
    assert "库存不足" in second.json()["message"]


def test_invalid_phone_rejected(client, seed):
    resp = client.post("/api/v1/orders", json=_order_payload(seed, customer_phone="12345"))
    assert resp.status_code == 422


def test_quantity_over_limit_rejected(client, seed):
    payload = _order_payload(seed, idempotency_key="qty-key-001", items=[{"menu_item_id": seed["item1_id"], "quantity": 100}])
    resp = client.post("/api/v1/orders", json=payload)
    assert resp.status_code == 422


def _create_order(client, seed, key):
    return client.post("/api/v1/orders", json=_order_payload(seed, idempotency_key=key))


def test_status_machine_allows_valid_and_rejects_invalid(client, seed):
    order_id = _create_order(client, seed, "state-key-001").json()["data"]["id"]
    headers = login(client, "admin1")

    bad = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"order_status": "completed"},
        headers=headers,
    )
    assert bad.status_code == 409

    ok1 = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"order_status": "accepted"},
        headers=headers,
    )
    assert ok1.status_code == 200

    cancelled = client.post(
        f"/api/v1/admin/orders/{order_id}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    assert cancelled.status_code == 200

    after_cancel = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"order_status": "completed"},
        headers=headers,
    )
    assert after_cancel.status_code == 409


def test_mark_paid_ok_and_cancelled_rejected(client, seed):
    order_id = _create_order(client, seed, "paid-key-001").json()["data"]["id"]
    headers = login(client, "admin1")
    resp = client.patch(f"/api/v1/admin/orders/{order_id}/payment", json={"payment_status": "paid"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["payment_status"] == "paid"

    order2_id = _create_order(client, seed, "paid-key-002").json()["data"]["id"]
    client.post(
        f"/api/v1/admin/orders/{order2_id}/cancel",
        json={"cancel_reason": "merchant_cancel_not_made"},
        headers=headers,
    )
    resp2 = client.patch(f"/api/v1/admin/orders/{order2_id}/payment", json={"payment_status": "paid"}, headers=headers)
    assert resp2.status_code == 409


def test_lookup_requires_phone_and_order_no(client, seed):
    order = _create_order(client, seed, "lookup-key-001").json()["data"]
    missing = client.get("/api/v1/orders", params={"phone": "13900000001"})
    assert missing.status_code == 422
    wrong = client.get("/api/v1/orders", params={"phone": "13900000002", "order_no": order["order_no"]})
    assert wrong.status_code == 404
    ok = client.get("/api/v1/orders", params={"phone": "13900000001", "order_no": order["order_no"]})
    assert ok.status_code == 200
    assert ok.json()["data"]["order_no"] == order["order_no"]


def test_admin_order_list_masks_phone_detail_full(client, seed):
    order = _create_order(client, seed, "mask-key-001").json()["data"]
    headers = login(client, "admin1")
    listing = client.get("/api/v1/admin/orders", headers=headers).json()["data"]
    assert listing[0]["customer_phone"] == "139****0001"
    detail = client.get(f"/api/v1/admin/orders/{order['id']}", headers=headers).json()["data"]
    assert detail["customer_phone"] == "13900000001"


def test_admin_order_scope_and_cross_store_blocked(client, seed):
    order1_id = _create_order(client, seed, "scope-key-001").json()["data"]["id"]
    order2 = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store2_id"],
            "customer_name": "万达顾客",
            "customer_phone": "13900000002",
            "idempotency_key": "scope-key-002",
            "items": [{"menu_item_id": seed["item3_id"], "quantity": 1}],
        },
    )
    assert order2.status_code == 201
    order2_id = order2.json()["data"]["id"]

    headers1 = login(client, "admin1")
    mine = client.get("/api/v1/admin/orders", headers=headers1).json()["data"]
    assert [order["id"] for order in mine] == [order1_id]

    detail = client.get(f"/api/v1/admin/orders/{order2_id}", headers=headers1)
    assert detail.status_code == 403


def test_orders_composite_index_exists(client, seed, db_session_factory):
    engine = db_session_factory().get_bind()
    indexes = {ix["name"]: ix for ix in inspect(engine).get_indexes("orders")}
    target = indexes.get("ix_orders_store_status_created")
    assert target is not None
    assert sorted(target["column_names"]) == ["created_at", "order_status", "store_id"]
