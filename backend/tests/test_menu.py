from tests.conftest import login


def test_public_menu_returns_groups_and_items(client, seed):
    resp = client.get(f"/api/v1/stores/{seed['store1_id']}/menu")
    assert resp.status_code == 200
    groups = resp.json()["data"]
    assert len(groups) == 1
    items = groups[0]["items"]
    assert {item["name"] for item in items} == {"招牌奶茶", "限量奶昔"}


def test_create_item_with_other_store_category_rejected(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/stores/{seed['store1_id']}/items",
        json={"name": "跨店商品", "price_cents": 900, "category_id": seed["cat2_id"]},
        headers=headers,
    )
    assert resp.status_code == 400


def test_admin_price_update_reflected_in_public_menu(client, seed):
    headers = login(client, "admin1")
    resp = client.put(
        f"/api/v1/admin/stores/{seed['store1_id']}/items/{seed['item1_id']}",
        json={"price_cents": 1500},
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item = next(i for i in menu[0]["items"] if i["id"] == seed["item1_id"])
    assert item["price_cents"] == 1500


def test_delete_item_soft_hides_from_public(client, seed):
    headers = login(client, "admin1")
    resp = client.delete(
        f"/api/v1/admin/stores/{seed['store1_id']}/items/{seed['item2_id']}",
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item_ids = {item["id"] for group in menu for item in group["items"]}
    assert seed["item2_id"] not in item_ids


def test_invalid_price_rejected(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        f"/api/v1/admin/stores/{seed['store1_id']}/items",
        json={"name": "零元商品", "price_cents": 0},
        headers=headers,
    )
    assert resp.status_code == 422


def test_admin2_cannot_edit_store1_menu(client, seed):
    headers = login(client, "admin2")
    resp = client.post(
        f"/api/v1/admin/stores/{seed['store1_id']}/categories",
        json={"name": "入侵分类"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_delete_category_deactivates_its_items(client, seed):
    headers = login(client, "admin1")
    resp = client.delete(
        f"/api/v1/admin/stores/{seed['store1_id']}/categories/{seed['cat1_id']}",
        headers=headers,
    )
    assert resp.status_code == 200
    menu = client.get(f"/api/v1/stores/{seed['store1_id']}/menu").json()["data"]
    item_ids = {item["id"] for group in menu for item in group["items"]}
    assert seed["item1_id"] not in item_ids
    order = client.post(
        "/api/v1/orders",
        json={
            "store_id": seed["store1_id"],
            "customer_name": "测试顾客",
            "customer_phone": "13900000001",
            "idempotency_key": "cat-inactive-key-001",
            "items": [{"menu_item_id": seed["item1_id"], "quantity": 1}],
        },
    )
    assert order.status_code == 400
