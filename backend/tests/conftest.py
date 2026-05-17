"""Pytest fixtures — configure isolated SQLite DB before importing app."""

import os
import sys
import uuid
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TEST_DB_DIR = BACKEND_ROOT / "database"
TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB_PATH = TEST_DB_DIR / "test_questions.db"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_PATH"] = str(TEST_DB_PATH)
os.environ["DB_TYPE"] = "sqlite"
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-for-unit-tests")
os.environ.setdefault("MINIMAX_API_KEY", "test-key-for-unit-tests")
os.environ.setdefault("FEISHU_APP_ID", "test")
os.environ.setdefault("FEISHU_APP_SECRET", "test")
os.environ.setdefault("FEISHU_VERIFICATION_TOKEN", "test")

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def _init_db():
    from src.database.db import init_database

    init_database()
    yield
    from src.database.db import db

    db.close()
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except OSError:
            pass


@pytest.fixture(scope="session")
def app(_init_db):
    from src.main import app as fastapi_app

    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unique_username():
    return f"user_{uuid.uuid4().hex[:12]}"


@pytest.fixture
def registered_user(client, unique_username):
    """Register a user and return credentials."""
    password = "TestPass123"
    resp = client.post(
        "/api/auth/register",
        json={"username": unique_username, "password": password, "nickname": "测试用户"},
    )
    assert resp.status_code == 200
    data = resp.json()
    return {
        "username": unique_username,
        "password": password,
        "user_id": data["user_id"],
        "token": data["token"],
    }


@pytest.fixture
def sample_question(client):
    """Insert a question via API."""
    payload = {
        "type": "single",
        "content": "单元测试题目：Cache 的主要作用是？",
        "options": {"A": "加速访问", "B": "扩容", "C": "降功耗", "D": "提高可靠性"},
        "answer": "A",
        "analysis": "Cache 用于加速 CPU 访问内存。",
        "knowledge_point": "1.1",
        "source": "unit-test",
        "status": "approved",
    }
    resp = client.post("/api/questions", json=payload)
    assert resp.status_code == 200
    qid = resp.json()["id"]
    return {"id": qid, **payload}


@pytest.fixture
def sample_knowledge_point():
    """Insert a knowledge point directly."""
    from src.modules.knowledge import knowledge_service

    code = f"T.{uuid.uuid4().hex[:6]}"
    kp_id = knowledge_service.create(
        {
            "code": code,
            "name": "测试知识点",
            "chapter": "测试章",
            "stage": "单元测试阶段",
            "sort_order": 9999,
            "status": "unlocked",
        }
    )
    return {"id": kp_id, "code": code}
