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
