"""Question service and API unit tests."""

from src.modules.question import question_service


class TestQuestionService:
    def test_create_and_get_by_id(self):
        q_id = question_service.create(
            {
                "type": "single",
                "content": "服务层测试题",
                "options": {"A": "a", "B": "b"},
                "answer": "A",
                "analysis": "解析",
                "knowledge_point": "svc-test",
                "source": "pytest-service",
                "status": "approved",
            }
        )
        assert q_id > 0
        q = question_service.get_by_id(q_id)
        assert q is not None
        assert q["content"] == "服务层测试题"
        assert q["options"]["A"] == "a"

    def test_list_all_with_filter(self):
        question_service.create(
            {
                "type": "judge",
                "content": "过滤测试题",
                "answer": "对",
                "source": "filter-source",
                "status": "pending",
            }
        )
        result = question_service.list_all({"source": "filter-source"}, page=1, page_size=10)
        assert result["total"] >= 1
        assert all(q["source"] == "filter-source" for q in result["data"])

    def test_update_and_delete(self):
        q_id = question_service.create(
            {"type": "single", "content": "待更新", "answer": "B", "source": "upd-del"}
        )
        assert question_service.update(q_id, {"content": "已更新", "status": "approved"})
        updated = question_service.get_by_id(q_id)
        assert updated["content"] == "已更新"
        assert question_service.delete(q_id)
        assert question_service.get_by_id(q_id) is None

    def test_batch_import(self):
        questions = [
            {"type": "single", "content": "导入1", "answer": "A", "options": {}},
            {"type": "single", "content": "导入2", "answer": "B", "options": {}},
        ]
        count = question_service.batch_import(questions, source="batch-import-test")
        assert count == 2

    def test_get_stats(self):
        stats = question_service.get_stats()
        assert "total" in stats
        assert "approved" in stats
        assert "pending" in stats
        assert "by_type" in stats


class TestQuestionsAPI:
    def test_create_question_via_api(self, client):
        resp = client.post(
            "/api/questions",
            json={
                "type": "single",
                "content": "API 创建题目",
                "options": {"A": "1", "B": "2"},
                "answer": "A",
                "source": "api-create",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["id"] > 0

    def test_list_questions_pagination(self, client, sample_question):
        resp = client.get("/api/questions?page=1&page_size=5&source=unit-test")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    def test_get_questions_by_knowledge_id_returns_data(self, client):
        resp = client.get("/api/questions/1")
        assert resp.status_code == 200
        assert "data" in resp.json()
