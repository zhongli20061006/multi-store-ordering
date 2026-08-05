from tests.conftest import login


def test_login_returns_token(client, seed):
    resp = client.post("/api/v1/auth/login", json={"username": "admin1", "password": "admin123456"})
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


def test_login_wrong_password_rejected(client, seed):
    resp = client.post("/api/v1/auth/login", json={"username": "admin1", "password": "wrong-password"})
    assert resp.status_code == 401


def test_me_requires_token(client, seed):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, seed):
    headers = login(client, "admin1")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "admin1"


def test_change_password_requires_old_password(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "wrong123", "new_password": "newpass123"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_change_password_success_and_old_password_invalid(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "admin123456", "new_password": "newpass123"},
        headers=headers,
    )
    assert resp.status_code == 200
    old = client.post("/api/v1/auth/login", json={"username": "admin1", "password": "admin123456"})
    assert old.status_code == 401
    new = client.post("/api/v1/auth/login", json={"username": "admin1", "password": "newpass123"})
    assert new.status_code == 200


def test_change_password_short_new_password_rejected(client, seed):
    headers = login(client, "admin1")
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "admin123456", "new_password": "123"},
        headers=headers,
    )
    assert resp.status_code == 422
