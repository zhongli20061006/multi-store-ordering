from tests.conftest import login

JPEG_BYTES = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffd9")
PNG_BYTES = bytes.fromhex("89504e470d0a1a0a0000000d49484452")


def _upload(client, headers, store_id, item_id, data, content_type):
    return client.post(
        f"/api/v1/admin/stores/{store_id}/items/{item_id}/image",
        content=data,
        headers={**headers, "Content-Type": content_type},
    )


def test_upload_item_image_sets_url_and_saves_file(client, seed, tmp_path, monkeypatch):
    import app.core.uploads as uploads

    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)
    headers = login(client, "admin1")
    resp = _upload(client, headers, seed["store1_id"], seed["item1_id"], JPEG_BYTES, "image/jpeg")
    assert resp.status_code == 200
    url = resp.json()["data"]["image_url"]
    assert url.startswith("/uploads/")
    assert (tmp_path / url.removeprefix("/uploads/")).exists()
    items = client.get(f"/api/v1/admin/stores/{seed['store1_id']}/items", headers=headers).json()["data"]
    assert next(i for i in items if i["id"] == seed["item1_id"])["image_url"] == url


def test_upload_item_image_cross_store_blocked(client, seed):
    headers = login(client, "admin2")
    resp = _upload(client, headers, seed["store1_id"], seed["item1_id"], JPEG_BYTES, "image/jpeg")
    assert resp.status_code == 403


def test_upload_item_image_rejects_wrong_content_type(client, seed):
    headers = login(client, "admin1")
    resp = _upload(client, headers, seed["store1_id"], seed["item1_id"], JPEG_BYTES, "text/plain")
    assert resp.status_code == 400


def test_upload_item_image_rejects_magic_mismatch(client, seed):
    headers = login(client, "admin1")
    resp = _upload(client, headers, seed["store1_id"], seed["item1_id"], b"not-an-image", "image/jpeg")
    assert resp.status_code == 400


def test_upload_item_image_rejects_oversize(client, seed):
    headers = login(client, "admin1")
    big = b"\xff\xd8\xff" + b"\x00" * (2 * 1024 * 1024 + 1)
    resp = _upload(client, headers, seed["store1_id"], seed["item1_id"], big, "image/jpeg")
    assert resp.status_code == 400


def test_clear_item_image_removes_url_and_file(client, seed, tmp_path, monkeypatch):
    import app.core.uploads as uploads

    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)
    headers = login(client, "admin1")
    uploaded = _upload(client, headers, seed["store1_id"], seed["item1_id"], PNG_BYTES, "image/png").json()["data"]
    assert uploaded["image_url"].endswith(".png")
    saved_path = tmp_path / uploaded["image_url"].removeprefix("/uploads/")
    assert saved_path.exists()
    resp = client.delete(f"/api/v1/admin/stores/{seed['store1_id']}/items/{seed['item1_id']}/image", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["image_url"] is None
    assert not saved_path.exists()
