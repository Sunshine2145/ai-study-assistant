"""Answer submission API unit tests."""


class TestAnswersAPI:
    def test_submit_correct_answer(self, client, registered_user, sample_question):
        q_id = sample_question["id"]
        resp = client.post(
            "/api/answers",
            json={"question_id": q_id, "answer": "A"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["correct"] is True
        assert data["correct_answer"] == "a"

    def test_submit_wrong_answer_records_wrong(self, client, sample_question):
        q_id = sample_question["id"]
        resp = client.post(
            "/api/answers",
            json={"question_id": q_id, "answer": "B"},
        )
        assert resp.status_code == 200
        assert resp.json()["correct"] is False

    def test_submit_nonexistent_question(self, client):
        resp = client.post(
            "/api/answers",
            json={"question_id": 999999, "answer": "A"},
        )
        assert resp.status_code == 200
        assert resp.json().get("error") == "题目不存在"

    def test_answer_stats(self, client, registered_user, sample_question):
        client.post(
            "/api/answers",
            json={"question_id": sample_question["id"], "answer": "A"},
        )
        resp = client.get("/api/answers/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total"] >= 1
        assert "correct" in stats
        assert "accuracy" in stats
