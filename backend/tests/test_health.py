def test_health_ok(client, seed):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ok"
