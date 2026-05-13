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
               FROM learning_progress WHERE user_id = %s AND knowledge_point_id = %s""",
            (user_id, knowledge_point_id)
        )
        if not result:
            return None
        history = result['socratic_history'] or '[]'
        try:
            history = json.loads(history)
        except (json.JSONDecodeError, TypeError):
            history = []
        return {
            "id": result['id'], "user_id": result['user_id'], "knowledge_point_id": result['knowledge_point_id'],
            "feynman_completed": result['feynman_completed'], "practice_completed": result['practice_completed'],
            "test_completed": result['test_completed'], "mastery_percentage": result['mastery_percentage'],
            "socratic_rounds": result['socratic_rounds'], "learning_phase": result['learning_phase'],
            "socratic_history": history
        }

    def update_phase(self, user_id: int, knowledge_point_id: int, phase: str):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, learning_phase, mastery_percentage, socratic_rounds)
            VALUES (%s, %s, %s, 0, 0)
            ON DUPLICATE KEY UPDATE
                learning_phase = VALUES(learning_phase), updated_at = NOW()
        """, (user_id, knowledge_point_id, phase))

    def update_mastery(self, user_id: int, knowledge_point_id: int, delta: int):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, mastery_percentage)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                mastery_percentage = LEAST(100, mastery_percentage + VALUES(mastery_percentage)),
                updated_at = NOW()
        """, (user_id, knowledge_point_id, delta))

    def record_socratic_round(self, user_id: int, knowledge_point_id: int):
        db.execute("""
            INSERT INTO learning_progress (user_id, knowledge_point_id, socratic_rounds, last_socratic_at)
            VALUES (%s, %s, 1, NOW())
            ON DUPLICATE KEY UPDATE
                socratic_rounds = socratic_rounds + 1,
                last_socratic_at = NOW(),
                updated_at = NOW()
        """, (user_id, knowledge_point_id))

    def check_unlock_threshold(self, knowledge_point_id: int) -> bool:
        result = db.fetch_one(
            "SELECT mastery_percentage FROM learning_progress WHERE knowledge_point_id = %s",
            (knowledge_point_id,)
        )
        return result and result['mastery_percentage'] >= 90

    def complete_and_unlock(self, knowledge_point_id: int):
        current_kp = db.fetch_one(
            "SELECT code, sort_order FROM knowledge_points WHERE id = %s",
            (knowledge_point_id,)
        )
        if not current_kp:
            return

        db.execute("UPDATE knowledge_points SET status = 'completed' WHERE id = %s", (knowledge_point_id,))

        next_kp = db.fetch_one("""
            SELECT id, code, name FROM knowledge_points
            WHERE sort_order > %s AND status = 'locked'
            ORDER BY sort_order LIMIT 1
        """, (current_kp['sort_order'],))

        if next_kp:
            db.execute("UPDATE knowledge_points SET status = 'unlocked' WHERE id = %s", (next_kp['id'],))
            logger.info(f"Unlocked next knowledge point: {next_kp['code']} - {next_kp['name']}")

    def get_user_stats(self, user_id: int) -> dict:
        user = db.fetch_one("SELECT score, streak FROM users WHERE id = %s", (user_id,))
        score = user['score'] if user else 0
        streak = user['streak'] if user else 0

        completed = db.fetch_one(
            "SELECT COUNT(*) as cnt FROM knowledge_points WHERE status = 'completed'"
        )['cnt'] or 0
        total = db.fetch_one("SELECT COUNT(*) as cnt FROM knowledge_points")['cnt'] or 0
        wrong_count = db.fetch_one(
            "SELECT COUNT(*) as cnt FROM wrong_questions WHERE user_id = %s AND mastered = 0",
            (user_id,)
        )['cnt'] or 0

        return {
            "score": score, "streak": streak,
            "completed_count": completed, "total_count": total,
            "wrong_count": wrong_count
        }

    def reset_progress(self, user_id: int):
        db.execute("UPDATE knowledge_points SET status = 'locked'")
        db.execute("DELETE FROM learning_progress WHERE user_id = %s", (user_id,))
        first_kp = db.fetch_one(
            "SELECT id FROM knowledge_points ORDER BY sort_order LIMIT 1"
        )
        if first_kp:
            db.execute("UPDATE knowledge_points SET status = 'unlocked' WHERE id = %s", (first_kp['id'],))


study_service = StudyService()
