from tests.conftest import login


def test_public_stores_lists_open_stores(client, seed):
    resp = client.get("/api/v1/stores")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


def test_public_store_detail_returns_fields(client, seed):
    resp = client.get(f"/api/v1/stores/{seed['store1_id']}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == seed["store1_id"]
    assert data["name"] == "中山路店"
    assert data["address"] == "中山路1号"
    assert data["phone"] == "13800000001"
    assert data["latitude"] is None
    assert data["longitude"] is None


def test_public_store_detail_not_found(client, seed):
    resp = client.get("/api/v1/stores/99999")
    assert resp.status_code == 404


def test_public_store_detail_returns_closed_store(client, seed):
    headers = login(client, "admin2")
    client.patch(
        f"/api/v1/admin/stores/{seed['store2_id']}/status",
        json={"status": "closed"},
        headers=headers,
    )
    resp = client.get(f"/api/v1/stores/{seed['store2_id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "closed"


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


def test_create_store_with_coordinates_ok(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={
            "name": "坐标店",
            "address": "某处",
            "phone": "13800000013",
            "sort_order": 7,
            "latitude": 30.2741,
            "longitude": 120.1551,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["latitude"] == 30.2741
    assert data["longitude"] == 120.1551


def test_create_store_rejects_partial_coordinates(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "半坐标", "address": "某处", "phone": "13800000014", "sort_order": 8, "latitude": 30.1},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "经纬度" in resp.json()["message"]


def test_create_store_rejects_out_of_range_coordinates(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/admin/stores",
        json={"name": "越界", "address": "某处", "phone": "13800000015", "sort_order": 9, "latitude": 91.0, "longitude": 120.0},
        headers=headers,
    )
    assert resp.status_code == 422


def test_update_store_coordinates_and_public_list_returns_them(client, seed):
    headers = login(client, "admin1")
    store_id = seed["store1_id"]
    resp = client.put(
        f"/api/v1/admin/stores/{store_id}",
        json={"latitude": 30.25, "longitude": 120.16},
        headers=headers,
    )
    assert resp.status_code == 200
    public = client.get("/api/v1/stores").json()["data"]
    target = next(store for store in public if store["id"] == store_id)
    assert target["latitude"] == 30.25
    assert target["longitude"] == 120.16
