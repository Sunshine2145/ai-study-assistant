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
                "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE stage = %s ORDER BY sort_order",
                (stage,)
            )
        else:
            results = db.fetch_all(
                "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points ORDER BY sort_order"
            )
        return [
            {"id": r['id'], "code": r['code'], "name": r['name'], "chapter": r['chapter'], "stage": r['stage'], "sort_order": r['sort_order'], "status": r['status']}
            for r in results
        ]

    def get_by_id(self, kp_id: int) -> Optional[dict]:
        result = db.fetch_one(
            "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE id = %s",
            (kp_id,)
        )
        if not result:
            return None
        return {"id": result['id'], "code": result['code'], "name": result['name'], "chapter": result['chapter'], "stage": result['stage'], "sort_order": result['sort_order'], "status": result['status']}

    def get_by_code(self, code: str) -> Optional[dict]:
        result = db.fetch_one(
            "SELECT id, code, name, chapter, stage, sort_order, status FROM knowledge_points WHERE code = %s",
            (code,)
        )
        if not result:
            return None
        return {"id": result['id'], "code": result['code'], "name": result['name'], "chapter": result['chapter'], "stage": result['stage'], "sort_order": result['sort_order'], "status": result['status']}

    def create(self, data: dict) -> int:
        existing = db.fetch_one("SELECT id FROM knowledge_points WHERE code = %s", (data["code"],))
        if existing:
            raise ValueError(f"知识点编码 {data['code']} 已存在")

        cursor = db.execute(
            """INSERT INTO knowledge_points (code, name, chapter, stage, sort_order, status)
               VALUES (%s, %s, %s, %s, %s, %s)""",
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
                fields.append(f"{key} = %s")
                values.append(data[key])

        if not fields:
            return False

        values.append(kp_id)
        db.execute(
            f"UPDATE knowledge_points SET {', '.join(fields)} WHERE id = %s",
            tuple(values)
        )
        return True

    def delete(self, kp_id: int) -> bool:
        existing = self.get_by_id(kp_id)
        if not existing:
            return False

        deps = db.fetch_one(
            "SELECT COUNT(*) as cnt FROM questions WHERE knowledge_point = %s",
            (str(kp_id),)
        )
        if deps and deps['cnt'] > 0:
            raise ValueError(f"该知识点下有 {deps['cnt']} 道题目，无法删除")

        db.execute("DELETE FROM knowledge_points WHERE id = %s", (kp_id,))
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
