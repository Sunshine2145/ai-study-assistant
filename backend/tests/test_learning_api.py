"""Learning progress API unit tests."""


class TestLearningAPI:
    def test_learning_status_empty_db_defaults(self, client):
        resp = client.get("/api/learning/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "completed_count" in data
        assert "total_count" in data
        assert "wrong_count" in data
        assert "current_knowledge" in data

    def test_learning_status_with_user_and_kp(self, client, registered_user, sample_knowledge_point):
        resp = client.get("/api/learning/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 1

    def test_get_current_knowledge(self, client, sample_knowledge_point):
        resp = client.get("/api/learning/current")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "code" in data
        assert "name" in data

    def test_select_unit(self, client, sample_knowledge_point):
        kp_id = sample_knowledge_point["id"]
        resp = client.post(f"/api/learning/select-unit/{kp_id}")
        assert resp.status_code == 200

    def test_mastery_endpoint(self, client, sample_knowledge_point):
        kp_id = sample_knowledge_point["id"]
        resp = client.get(f"/api/learning/mastery/{kp_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "mastery_percentage" in data
