# AI Study Assistant - Answers Routes

from fastapi import APIRouter
from pydantic import BaseModel

from src.database.db import db

router = APIRouter(prefix="/api/answers", tags=["答题"])


class AnswerRequest(BaseModel):
    question_id: int
    answer: str


@router.post("")
async def submit_answer(request: AnswerRequest):
    """提交答案"""
    # 获取正确答案
    result = db.fetch_one(
        "SELECT answer, knowledge_point FROM questions WHERE id = ?",
        (request.question_id,)
    )

    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    user_id = user[0] if user else 1

    if result:
        correct_answer = str(result[0]).strip().lower()
        user_answer = str(request.answer).strip().lower()
        is_correct = user_answer == correct_answer

        # 记录答题结果
        db.execute(
            """INSERT INTO answer_records (user_id, question_id, user_answer, is_correct)
               VALUES (?, ?, ?, ?)""",
            (user_id, request.question_id, request.answer, 1 if is_correct else 0)
        )

        # 如果答错，记录到错题本
        if not is_correct:
            existing = db.fetch_one(
                "SELECT id, wrong_count FROM wrong_questions WHERE user_id = ? AND question_id = ?",
                (user_id, request.question_id)
            )
            if existing:
                db.execute(
                    "UPDATE wrong_questions SET wrong_count = wrong_count + 1, last_wrong_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (existing[0],)
                )
            else:
                db.execute(
                    "INSERT INTO wrong_questions (user_id, question_id) VALUES (?, ?)",
                    (user_id, request.question_id)
                )

        # 更新用户积分
        if is_correct:
            db.execute("UPDATE users SET score = score + 10 WHERE id = ?", (user_id,))

        return {
            "correct": is_correct,
            "correct_answer": correct_answer
        }

    return {"correct": False, "error": "题目不存在"}


@router.get("/stats")
async def get_answer_stats():
    """获取答题统计"""
    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    user_id = user[0] if user else 1

    total = db.fetch_one(
        "SELECT COUNT(*) FROM answer_records WHERE user_id = ?",
        (user_id,)
    )[0] or 0

    correct = db.fetch_one(
        "SELECT COUNT(*) FROM answer_records WHERE user_id = ? AND is_correct = 1",
        (user_id,)
    )[0] or 0

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total * 100, 1) if total > 0 else 0
    }