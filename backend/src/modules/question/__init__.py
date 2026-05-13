# AI Study Assistant - Question Module

import json
from typing import Optional
from loguru import logger

from src.database.db import db


class QuestionService:
    """Service for question CRUD operations"""

    def list_all(self, filters: dict = None, page: int = 1, page_size: int = 20) -> dict:
        filters = filters or {}
        conditions = []
        params = []

        if filters.get("source"):
            conditions.append("source = %s")
            params.append(filters["source"])
        if filters.get("knowledge_point"):
            conditions.append("knowledge_point = %s")
            params.append(filters["knowledge_point"])
        if filters.get("type"):
            conditions.append("type = %s")
            params.append(filters["type"])
        if filters.get("status"):
            conditions.append("status = %s")
            params.append(filters["status"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        count_result = db.fetch_one(f"SELECT COUNT(*) as cnt FROM questions WHERE {where_clause}", tuple(params))
        total = count_result['cnt'] if count_result else 0

        offset = (page - 1) * page_size
        results = db.fetch_all(
            f"""SELECT id, type, content, options, answer, analysis, knowledge_point, difficulty, source, status, created_at
                FROM questions WHERE {where_clause} ORDER BY id DESC LIMIT %s OFFSET %s""",
            tuple(params) + (page_size, offset)
        )

        questions = []
        for r in results:
            options = r['options'] or '{}'
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = {}
            questions.append({
                "id": r['id'], "type": r['type'], "content": r['content'], "options": options,
                "answer": r['answer'], "analysis": r['analysis'], "knowledge_point": r['knowledge_point'],
                "difficulty": r['difficulty'], "source": r['source'], "status": r['status'], "created_at": r['created_at']
            })

        return {
            "data": questions, "total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }

    def get_by_id(self, question_id: int) -> Optional[dict]:
        result = db.fetch_one(
            """SELECT id, type, content, options, answer, analysis, knowledge_point, difficulty, source, status
               FROM questions WHERE id = %s""",
            (question_id,)
        )
        if not result:
            return None
        options = result['options'] or '{}'
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except:
                options = {}
        return {
            "id": result['id'], "type": result['type'], "content": result['content'], "options": options,
            "answer": result['answer'], "analysis": result['analysis'], "knowledge_point": result['knowledge_point'],
            "difficulty": result['difficulty'], "source": result['source'], "status": result['status']
        }

    def create(self, data: dict) -> int:
        options_json = json.dumps(data.get("options", {}), ensure_ascii=False)
        cursor = db.execute(
            """INSERT INTO questions (type, content, options, answer, analysis, knowledge_point, difficulty, source, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.get("type", "single"), data.get("content", ""), options_json,
             data.get("answer", ""), data.get("analysis", ""),
             data.get("knowledge_point", ""), data.get("difficulty", 1),
             data.get("source", "manual"), data.get("status", "pending"))
        )
        return cursor.lastrowid

    def update(self, question_id: int, data: dict) -> bool:
        existing = self.get_by_id(question_id)
        if not existing:
            return False

        fields = []
        values = []
        for key in ["type", "content", "answer", "analysis", "knowledge_point", "difficulty", "source", "status"]:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if "options" in data:
            fields.append("options = %s")
            values.append(json.dumps(data["options"], ensure_ascii=False))

        if not fields:
            return False

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(question_id)
        db.execute(f"UPDATE questions SET {', '.join(fields)} WHERE id = %s", tuple(values))
        return True

    def delete(self, question_id: int) -> bool:
        existing = self.get_by_id(question_id)
        if not existing:
            return False
        db.execute("DELETE FROM answer_records WHERE question_id = %s", (question_id,))
        db.execute("DELETE FROM wrong_questions WHERE question_id = %s", (question_id,))
        db.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        return True

    def update_status(self, question_id: int, status: str) -> bool:
        existing = self.get_by_id(question_id)
        if not existing:
            return False
        db.execute("UPDATE questions SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (status, question_id))
        return True

    def batch_import(self, questions: list, knowledge_point: Optional[str] = None, source: str = "manual") -> int:
        imported = 0
        for q in questions:
            try:
                options_json = json.dumps(q.get("options", {}), ensure_ascii=False)
                db.execute(
                    """INSERT INTO questions (type, content, options, answer, analysis, knowledge_point, source, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 'approved')""",
                    (q.get("type", "single"), q.get("content", ""), options_json,
                     str(q.get("answer", "")), q.get("analysis", ""),
                     knowledge_point or q.get("knowledge_point", ""), source)
                )
                imported += 1
            except Exception:
                continue
        return imported

    def get_stats(self) -> dict:
        total = db.fetch_one("SELECT COUNT(*) as cnt FROM questions")['cnt'] or 0
        approved = db.fetch_one("SELECT COUNT(*) as cnt FROM questions WHERE status = 'approved'")['cnt'] or 0
        pending = db.fetch_one("SELECT COUNT(*) as cnt FROM questions WHERE status = 'pending'")['cnt'] or 0
        by_type = db.fetch_all("SELECT type, COUNT(*) as cnt FROM questions GROUP BY type")
        by_source = db.fetch_all("SELECT source, COUNT(*) as cnt FROM questions GROUP BY source ORDER BY cnt DESC LIMIT 10")
        return {
            "total": total, "approved": approved, "pending": pending,
            "by_type": [{"type": r['type'], "count": r['cnt']} for r in by_type],
            "by_source": [{"source": r['source'] or "未分类", "count": r['cnt']} for r in by_source]
        }

    def get_by_source(self, source: str, page: int = 1, page_size: int = 20) -> dict:
        return self.list_all(filters={"source": source}, page=page, page_size=page_size)

    def get_banks(self) -> list:
        results = db.fetch_all(
            """SELECT source, COUNT(*) as cnt, SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_cnt
               FROM questions GROUP BY source ORDER BY cnt DESC"""
        )
        return [
            {"source": r['source'] or "未分类", "total": r['cnt'] or 0, "approved": r['approved_cnt'] or 0, "pending": (r['cnt'] or 0) - (r['approved_cnt'] or 0)}
            for r in results
        ]

    def delete_by_source(self, source: str) -> int:
        """Delete all questions with the given source. Returns count of deleted questions."""
        # Handle "未分类" which maps to NULL in database
        if source == "未分类":
            count = db.fetch_one("SELECT COUNT(*) as cnt FROM questions WHERE source IS NULL")['cnt'] or 0
            rows = db.fetch_all("SELECT id FROM questions WHERE source IS NULL")
            for row in rows:
                db.execute("DELETE FROM answer_records WHERE question_id = %s", (row['id'],))
                db.execute("DELETE FROM wrong_questions WHERE question_id = %s", (row['id'],))
            db.execute("DELETE FROM questions WHERE source IS NULL")
        else:
            count = db.fetch_one("SELECT COUNT(*) as cnt FROM questions WHERE source = %s", (source,))['cnt'] or 0
            rows = db.fetch_all("SELECT id FROM questions WHERE source = %s", (source,))
            for row in rows:
                db.execute("DELETE FROM answer_records WHERE question_id = %s", (row['id'],))
                db.execute("DELETE FROM wrong_questions WHERE question_id = %s", (row['id'],))
            db.execute("DELETE FROM questions WHERE source = %s", (source,))
        return count


question_service = QuestionService()
