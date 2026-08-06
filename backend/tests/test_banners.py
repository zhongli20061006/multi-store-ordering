from tests.conftest import login

JPEG_BYTES = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffd9")
PNG_BYTES = bytes.fromhex("89504e470d0a1a0a0000000d49484452")


def _upload(client, headers, store_id, data, content_type):
    return client.post(
        f"/api/v1/admin/stores/{store_id}/banners",
        content=data,
        headers={**headers, "Content-Type": content_type},
    )


def test_create_banner_uploads_and_lists(client, seed, tmp_path, monkeypatch):
    import app.core.uploads as uploads

    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)
    headers = login(client, "admin1")
    created = _upload(client, headers, seed["store1_id"], JPEG_BYTES, "image/jpeg")
    assert created.status_code == 201
    banner = created.json()["data"]
    assert banner["image_url"].startswith("/uploads/")
    assert (tmp_path / banner["image_url"].removeprefix("/uploads/")).exists()

    public = client.get(f"/api/v1/stores/{seed['store1_id']}/banners").json()["data"]
    assert [b["id"] for b in public] == [banner["id"]]
    mine = client.get(f"/api/v1/admin/stores/{seed['store1_id']}/banners", headers=headers).json()["data"]
    assert [b["id"] for b in mine] == [banner["id"]]


def test_banner_cross_store_blocked(client, seed):
    headers = login(client, "admin2")
    resp = _upload(client, headers, seed["store1_id"], JPEG_BYTES, "image/jpeg")
    assert resp.status_code == 403


def test_banner_rejects_non_image(client, seed):
    headers = login(client, "admin1")
    resp = _upload(client, headers, seed["store1_id"], b"not-image", "text/plain")
    assert resp.status_code == 400


def test_banner_toggle_and_reorder(client, seed):
    headers = login(client, "admin1")
    b1 = _upload(client, headers, seed["store1_id"], JPEG_BYTES, "image/jpeg").json()["data"]
    b2 = _upload(client, headers, seed["store1_id"], PNG_BYTES, "image/png").json()["data"]
    client.put(
        f"/api/v1/admin/stores/{seed['store1_id']}/banners/{b1['id']}",
        json={"sort_order": 10},
        headers=headers,
    )
    public = client.get(f"/api/v1/stores/{seed['store1_id']}/banners").json()["data"]
    assert [b["id"] for b in public] == [b2["id"], b1["id"]]
    client.put(
        f"/api/v1/admin/stores/{seed['store1_id']}/banners/{b2['id']}",
        json={"is_active": False},
        headers=headers,
    )
    public2 = client.get(f"/api/v1/stores/{seed['store1_id']}/banners").json()["data"]
    assert [b["id"] for b in public2] == [b1["id"]]


def test_delete_banner_removes_row_and_file(client, seed, tmp_path, monkeypatch):
    import app.core.uploads as uploads

    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)
    headers = login(client, "admin1")
    banner = _upload(client, headers, seed["store1_id"], JPEG_BYTES, "image/jpeg").json()["data"]
    saved = tmp_path / banner["image_url"].removeprefix("/uploads/")
    assert saved.exists()
    resp = client.delete(f"/api/v1/admin/stores/{seed['store1_id']}/banners/{banner['id']}", headers=headers)
    assert resp.status_code == 200
    assert not saved.exists()
    public = client.get(f"/api/v1/stores/{seed['store1_id']}/banners").json()["data"]
    assert public == []
