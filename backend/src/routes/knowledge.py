# AI Study Assistant - Knowledge Routes

from fastapi import APIRouter
from typing import Optional

from src.database.db import db

router = APIRouter(prefix="/api/knowledge", tags=["知识点"])


@router.get("")
async def get_knowledge_points(stage: Optional[str] = None):
    """获取知识点列表"""
    if stage:
        results = db.fetch_all(
            "SELECT id, code, name, chapter, stage, status FROM knowledge_points WHERE stage = ? ORDER BY sort_order",
            (stage,)
        )
    else:
        results = db.fetch_all(
            "SELECT id, code, name, chapter, stage, status FROM knowledge_points ORDER BY sort_order"
        )

    return {
        "data": [
            {
                "id": r[0],
                "code": r[1],
                "name": r[2],
                "chapter": r[3],
                "stage": r[4],
                "status": r[5]
            }
            for r in results
        ]
    }


@router.get("/{code}")
async def get_knowledge_point(code: str):
    """获取指定知识点"""
    result = db.fetch_one(
        "SELECT id, code, name, chapter, stage, status FROM knowledge_points WHERE code = ?",
        (code,)
    )
    if not result:
        return {"error": "知识点不存在"}

    return {
        "id": result[0],
        "code": result[1],
        "name": result[2],
        "chapter": result[3],
        "stage": result[4],
        "status": result[5]
    }