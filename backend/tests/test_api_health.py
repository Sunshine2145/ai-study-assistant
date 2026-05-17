"""Core API health and root endpoint tests."""


class TestHealthEndpoints:
    def test_root_returns_api_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "AI伴学系统 API"
        assert body["version"] == "1.0.0"

    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
