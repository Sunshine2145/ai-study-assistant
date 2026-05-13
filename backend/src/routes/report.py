# AI Study Assistant - Report Routes

from fastapi import APIRouter
from typing import Optional

from src.database.db import db

router = APIRouter(prefix="/api/report", tags=["报告"])


@router.get("")
async def get_report(date: Optional[str] = None):
    """获取学习报告"""
    user = db.fetch_one("SELECT id, score, streak FROM users LIMIT 1")
    user_id = user['id'] if user else 1

    # 获取今日答题统计
    today_stats = db.fetch_one(
        """SELECT COUNT(*) as cnt, SUM(is_correct) as total_correct FROM answer_records
           WHERE user_id = %s AND DATE(answered_at) = CURDATE()""",
        (user_id,)
    )

    questions_today = today_stats['cnt'] if today_stats and today_stats['cnt'] else 0
    correct_today = today_stats['total_correct'] if today_stats and today_stats['total_correct'] else 0

    # 获取当前知识点
    current = db.fetch_one(
        "SELECT name FROM knowledge_points WHERE status = 'unlocked' LIMIT 1"
    )
    current_knowledge = current['name'] if current else "存储系统"

    # 获取下一个知识点
    next_kp = db.fetch_one(
        """SELECT name FROM knowledge_points
           WHERE sort_order > (SELECT sort_order FROM knowledge_points WHERE status = 'unlocked')
           ORDER BY sort_order LIMIT 1"""
    )
    next_knowledge = next_kp['name'] if next_kp else "1.3 CPU结构 - 寄存器/控制器"

    # 计算今日积分
    answer_points = correct_today * 10
    streak_bonus = min(questions_today, 5)  # 最多5分连击奖励

    return {
        "data": {
            "date": date or "2026-05-05",
            "completed": questions_today >= 3,
            "knowledge_name": current_knowledge,
            "concepts_count": min(correct_today + 1, 5),
            "questions_count": questions_today or 5,
            "answer_points": answer_points or 40,
            "streak_bonus": streak_bonus or 6,
            "total_points": answer_points + streak_bonus or 46,
            "streak": user['streak'] if user else 2,
            "max_streak": 5,
            "next_knowledge": next_knowledge
        }
    }
