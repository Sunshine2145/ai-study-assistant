# AI Study Assistant - Knowledge Module

import json
from typing import Optional
from loguru import logger

from src.database.db import db


class KnowledgePointService:
    """Service for knowledge point CRUD operations"""

    def list_all(self, stage: Optional[str] = None) -> list:
        if stage:
            results = db.fetch_all(
                "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE stage = ? ORDER BY sort_order",
                (stage,)
            )
        else:
            results = db.fetch_all(
                "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points ORDER BY sort_order"
            )
        return [
            {"id": r[0], "code": r[1], "name": r[2], "chapter": r[3], "stage": r[4], "sort_order": r[5], "status": r[6]}
            for r in results
        ]

    def get_by_id(self, kp_id: int) -> Optional[dict]:
        result = db.fetch_one(
            "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE id = ?",
            (kp_id,)
        )
        if not result:
            return None
        return {"id": result[0], "code": result[1], "name": result[2], "chapter": result[3], "stage": result[4], "sort_order": result[5], "status": result[6]}

    def get_by_code(self, code: str) -> Optional[dict]:
        result = db.fetch_one(
            "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE code = ?",
            (code,)
        )
        if not result:
            return None
        return {"id": result[0], "code": result[1], "name": result[2], "chapter": result[3], "stage": result[4], "sort_order": result[5], "status": result[6]}

    def create(self, data: dict) -> int:
        existing = db.fetch_one("SELECT id FROM knowledge_points WHERE code = ?", (data["code"],))
        if existing:
            raise ValueError(f"知识点编码 {data['code']} 已存在")

        cursor = db.execute(
            """INSERT INTO knowledge_points (code, name, chapter, stage, sort_order, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data["code"], data["name"], data.get("chapter", ""), data.get("stage", ""),
             data.get("sort_order", 0), data.get("status", "locked"))
        )
        return cursor.lastrowid

    def update(self, kp_id: int, data: dict) -> bool:
        existing = self.get_by_id(kp_id)
        if not existing:
            return False

        fields = []
        values = []
        for key in ["code", "name", "chapter", "stage", "sort_order", "status"]:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])

        if not fields:
            return False

        values.append(kp_id)
        db.execute(
            f"UPDATE knowledge_points SET {', '.join(fields)} WHERE id = ?",
            tuple(values)
        )
        return True

    def delete(self, kp_id: int) -> bool:
        existing = self.get_by_id(kp_id)
        if not existing:
            return False

        deps = db.fetch_one(
            "SELECT COUNT(*) FROM questions WHERE knowledge_point = ?",
            (str(kp_id),)
        )
        if deps and deps[0] > 0:
            raise ValueError(f"该知识点下有 {deps[0]} 道题目，无法删除")

        db.execute("DELETE FROM knowledge_points WHERE id = ?", (kp_id,))
        return True

    def batch_import(self, items: list) -> int:
        imported = 0
        for item in items:
            try:
                self.create(item)
                imported += 1
            except (ValueError, Exception) as e:
                logger.warning(f"Skip knowledge point: {e}")
                continue
        return imported

    def export_all(self) -> list:
        return self.list_all()


knowledge_service = KnowledgePointService()
