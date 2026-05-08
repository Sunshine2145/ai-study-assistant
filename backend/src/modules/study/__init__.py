# AI Study Assistant - Study Module

import json
from typing import Optional
from loguru import logger

from src.database.db import db


class StudyService:
    """Service for study session and progress management"""

    def get_session(self, user_id: int, knowledge_point_id: int) -> Optional[dict]:
        result = db.fetch_one(
            """SELECT id, user_id, knowledge_point_id, feynman_completed, practice_completed,
                      test_completed, mastery_percentage, socratic_rounds, learning_phase, socratic_history
               FROM learning_progress WHERE user_id = ? AND knowledge_point_id = ?""",
            (user_id, knowledge_point_id)
        )
        if not result:
            return None
        history = result[9] or '[]'
        try:
            history = json.loads(history)
        except (json.JSONDecodeError, TypeError):
            history = []
        return {
            "id": result[0], "user_id": result[1], "knowledge_point_id": result[2],
            "feynman_completed": result[3], "practice_completed": result[4],
            "test_completed": result[5], "mastery_percentage": result[6],
            "socratic_rounds": result[7], "learning_phase": result[8],
            "socratic_history": history
        }

    def update_phase(self, user_id: int, knowledge_point_id: int, phase: str):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, learning_phase, mastery_percentage, socratic_rounds)
            VALUES (?, ?, ?, 0, 0)
            ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
            learning_phase = ?, updated_at = CURRENT_TIMESTAMP
        """, (user_id, knowledge_point_id, phase, phase))

    def update_mastery(self, user_id: int, knowledge_point_id: int, delta: int):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, mastery_percentage)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
            mastery_percentage = MIN(100, mastery_percentage + ?),
            updated_at = CURRENT_TIMESTAMP
        """, (user_id, knowledge_point_id, delta, delta))

    def record_socratic_round(self, user_id: int, knowledge_point_id: int):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, socratic_rounds, last_socratic_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
            socratic_rounds = socratic_rounds + 1,
            last_socratic_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        """, (user_id, knowledge_point_id))

    def check_unlock_threshold(self, knowledge_point_id: int) -> bool:
        result = db.fetch_one(
            "SELECT mastery_percentage FROM learning_progress WHERE knowledge_point_id = ?",
            (knowledge_point_id,)
        )
        return result and result[0] >= 90

    def complete_and_unlock(self, knowledge_point_id: int):
        current_kp = db.fetch_one(
            "SELECT code, sort_order FROM knowledge_points WHERE id = ?",
            (knowledge_point_id,)
        )
        if not current_kp:
            return

        db.execute("UPDATE knowledge_points SET status = 'completed' WHERE id = ?", (knowledge_point_id,))

        next_kp = db.fetch_one("""
            SELECT id, code, name FROM knowledge_points
            WHERE sort_order > ? AND status = 'locked'
            ORDER BY sort_order LIMIT 1
        """, (current_kp[1],))

        if next_kp:
            db.execute("UPDATE knowledge_points SET status = 'unlocked' WHERE id = ?", (next_kp[0],))
            logger.info(f"Unlocked next knowledge point: {next_kp[1]} - {next_kp[2]}")

    def get_user_stats(self, user_id: int) -> dict:
        user = db.fetch_one("SELECT score, streak FROM users WHERE id = ?", (user_id,))
        score = user[0] if user else 0
        streak = user[1] if user else 0

        completed = db.fetch_one(
            "SELECT COUNT(*) FROM knowledge_points WHERE status = 'completed'"
        )[0] or 0
        total = db.fetch_one("SELECT COUNT(*) FROM knowledge_points")[0] or 0
        wrong_count = db.fetch_one(
            "SELECT COUNT(*) FROM wrong_questions WHERE user_id = ? AND mastered = 0",
            (user_id,)
        )[0] or 0

        return {
            "score": score, "streak": streak,
            "completed_count": completed, "total_count": total,
            "wrong_count": wrong_count
        }

    def reset_progress(self, user_id: int):
        db.execute("UPDATE knowledge_points SET status = 'locked'")
        db.execute("DELETE FROM learning_progress WHERE user_id = ?", (user_id,))
        first_kp = db.fetch_one(
            "SELECT id FROM knowledge_points ORDER BY sort_order LIMIT 1"
        )
        if first_kp:
            db.execute("UPDATE knowledge_points SET status = 'unlocked' WHERE id = ?", (first_kp[0],))


study_service = StudyService()
