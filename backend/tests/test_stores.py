from tests.conftest import login


def test_public_stores_lists_open_stores(client, seed):
    resp = client.get("/api/v1/stores")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


def test_closed_store_hidden_from_public(client, seed):
    headers = login(client, "admin2")
    resp = client.patch(
        f"/api/v1/admin/stores/{seed['store2_id']}/status",
        json={"status": "closed"},
        headers=headers,
    )
    assert resp.status_code == 200
    public = client.get("/api/v1/stores").json()["data"]
    assert [store["id"] for store in public] == [seed["store1_id"]]


def test_admin_sees_only_own_stores(client, seed):
    headers = login(client, "admin1")
    resp = client.get("/api/v1/admin/stores", headers=headers)
    assert resp.status_code == 200
    assert [store["id"] for store in resp.json()["data"]] == [seed["store1_id"]]


def test_admin_cannot_operate_other_store(client, seed):
    headers = login(client, "admin1")
    resp = client.patch(
        f"/api/v1/admin/stores/{seed['store2_id']}/status",
        json={"status": "closed"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_admin_endpoint_requires_login(client, seed):
    resp = client.get("/api/v1/admin/stores")
    assert resp.status_code == 401


def test_create_store_binds_to_admin(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "新门店", "address": "某处", "phone": "13800000009", "sort_order": 3},
        headers=headers,
    )
    assert resp.status_code == 201
    new_store_id = resp.json()["data"]["id"]
    mine = client.get("/api/v1/admin/stores", headers=headers).json()["data"]
    assert new_store_id in [store["id"] for store in mine]
    other = login(client, "admin2")
    theirs = client.get("/api/v1/admin/stores", headers=other).json()["data"]
    assert new_store_id not in [store["id"] for store in theirs]


def test_delete_store_with_orders_rejected(client, seed):
    resp = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": "delete-store-test-key-001",
            "items": [{"menu_item_id": seed["item1_id"], "quantity": 1}],
        },
    )
    assert resp.status_code == 201
    headers = login(client, "admin1")
    resp = client.delete(f"/api/v1/admin/stores/{seed['store1_id']}", headers=headers)
    assert resp.status_code == 409


def test_create_store_with_hours_ok(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "小时店", "address": "某处", "phone": "13800000010", "sort_order": 4, "open_time": "09:00", "close_time": "22:00"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["open_time"] == "09:00"
    assert resp.json()["data"]["close_time"] == "22:00"


def test_create_store_rejects_invalid_hours_format(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "坏小时", "address": "某处", "phone": "13800000011", "sort_order": 5, "open_time": "25:00", "close_time": "22:00"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_create_store_rejects_invalid_hours_range(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "倒挂", "address": "某处", "phone": "13800000012", "sort_order": 6, "open_time": "22:00", "close_time": "09:00"},
        headers=headers,
    )
    assert resp.status_code == 400
