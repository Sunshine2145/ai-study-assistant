# AI Study Assistant - Wrong Questions Routes

from fastapi import APIRouter
from typing import Optional

from src.database.db import db

router = APIRouter(prefix="/api/wrong-questions", tags=["错题"])


@router.get("")
async def get_wrong_questions(filter: str = "week"):
    """获取错题列表"""
    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    user_id = user[0] if user else 1

    if filter == "all":
        results = db.fetch_all(
            """SELECT w.id, q.content, q.answer, q.analysis, w.wrong_count, w.last_wrong_at, k.name, a.user_answer
               FROM wrong_questions w
               JOIN questions q ON w.question_id = q.id
               LEFT JOIN knowledge_points k ON q.knowledge_point = k.code
               LEFT JOIN answer_records a ON a.question_id = w.question_id AND a.user_id = w.user_id AND a.is_correct = 0
               WHERE w.user_id = ? AND w.mastered = 0
               ORDER BY w.last_wrong_at DESC""",
            (user_id,)
        )
    elif filter == "month":
        results = db.fetch_all(
            """SELECT w.id, q.content, q.answer, q.analysis, w.wrong_count, w.last_wrong_at, k.name, a.user_answer
               FROM wrong_questions w
               JOIN questions q ON w.question_id = q.id
               LEFT JOIN knowledge_points k ON q.knowledge_point = k.code
               LEFT JOIN answer_records a ON a.question_id = w.question_id AND a.user_id = w.user_id AND a.is_correct = 0
               WHERE w.user_id = ? AND w.mastered = 0
               AND w.last_wrong_at > datetime('now', '-30 days')
               ORDER BY w.last_wrong_at DESC""",
            (user_id,)
        )
    else:  # week
        results = db.fetch_all(
            """SELECT w.id, q.content, q.answer, q.analysis, w.wrong_count, w.last_wrong_at, k.name, a.user_answer
               FROM wrong_questions w
               JOIN questions q ON w.question_id = q.id
               LEFT JOIN knowledge_points k ON q.knowledge_point = k.code
               LEFT JOIN answer_records a ON a.question_id = w.question_id AND a.user_id = w.user_id AND a.is_correct = 0
               WHERE w.user_id = ? AND w.mastered = 0
               AND w.last_wrong_at > datetime('now', '-7 days')
               ORDER BY w.last_wrong_at DESC""",
            (user_id,)
        )

    if not results:
        # 返回示例数据
        return {
            "data": [
                {
                    "id": 1,
                    "knowledge_name": "存储系统",
                    "question_content": "Cache的主要作用是什么？",
                    "user_answer": "加快硬盘速度",
                    "correct_answer": "加快CPU访问内存速度",
                    "wrong_date": "2026-05-04"
                },
                {
                    "id": 2,
                    "knowledge_name": "指令系统",
                    "question_content": "下列关于RISC的说法，错误的是？",
                    "user_answer": "指令长度固定",
                    "correct_answer": "指令格式简单，寻址方式少",
                    "wrong_date": "2026-05-05"
                }
            ]
        }

    return {
        "data": [
            {
                "id": r[0],
                "question_content": r[1],
                "correct_answer": r[2],
                "analysis": r[3],
                "wrong_count": r[4],
                "wrong_date": r[5].split()[0] if r[5] else "",
                "knowledge_name": r[6],
                "user_answer": r[7] or "未知"
            }
            for r in results
        ]
    }


@router.post("/{id}/master")
async def mark_as_mastered(id: int):
    """标记已掌握"""
    db.execute(
        "UPDATE wrong_questions SET mastered = 1, mastered_at = CURRENT_TIMESTAMP WHERE id = ?",
        (id,)
    )
    return {"message": "已标记为掌握"}


@router.delete("/{id}")
async def delete_wrong_question(id: int):
    """删除错题记录"""
    db.execute("DELETE FROM wrong_questions WHERE id = ?", (id,))
    return {"message": "已删除"}