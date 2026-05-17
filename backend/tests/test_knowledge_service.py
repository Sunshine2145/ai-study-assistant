"""Knowledge point service and API unit tests."""

import uuid

import pytest

from src.modules.knowledge import knowledge_service


class TestKnowledgeService:
    def test_create_get_update_delete(self):
        code = f"KP.{uuid.uuid4().hex[:8]}"
        kp_id = knowledge_service.create(
            {
                "code": code,
                "name": "CRUD 测试",
                "chapter": "章",
                "stage": "阶段",
                "sort_order": 1,
                "status": "locked",
            }
        )
        assert kp_id > 0

        by_code = knowledge_service.get_by_code(code)
        assert by_code["name"] == "CRUD 测试"

        assert knowledge_service.update(kp_id, {"status": "unlocked", "name": "已更新"})
        updated = knowledge_service.get_by_id(kp_id)
        assert updated["status"] == "unlocked"
        assert updated["name"] == "已更新"

        assert knowledge_service.delete(kp_id)
        assert knowledge_service.get_by_id(kp_id) is None

    def test_create_duplicate_code_raises(self):
        code = f"DUP.{uuid.uuid4().hex[:8]}"
        knowledge_service.create({"code": code, "name": "第一次"})
        with pytest.raises(ValueError, match="已存在"):
            knowledge_service.create({"code": code, "name": "第二次"})


class TestKnowledgeAPI:
    def test_list_knowledge_points(self, client, sample_knowledge_point):
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        assert "data" in resp.json()
        assert len(resp.json()["data"]) >= 1

    def test_get_knowledge_by_code(self, client, sample_knowledge_point):
        code = sample_knowledge_point["code"]
        resp = client.get(f"/api/knowledge/{code}")
        assert resp.status_code == 200
        assert resp.json()["code"] == code

    def test_get_nonexistent_knowledge_returns_404(self, client):
        resp = client.get("/api/knowledge/NOT.EXIST.CODE")
        assert resp.status_code == 404
