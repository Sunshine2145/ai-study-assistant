# AI Study Assistant - Reminders Routes

from fastapi import APIRouter

from src.database.db import db

router = APIRouter(prefix="/api/reminders", tags=["提醒"])


@router.get("")
async def get_reminders():
    """获取提醒列表"""
    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    user_id = user['id'] if user else 1

    results = db.fetch_all(
        """SELECT id, type, trigger_time, message_template, enabled
           FROM reminder_rules WHERE user_id = %s AND enabled = 1""",
        (user_id,)
    )

    if not results:
        # 返回示例提醒
        return [
            {"id": 1, "type": "daily", "time": "09:00", "message": "今天也要继续学习哦！"},
            {"id": 2, "type": "streak", "time": "20:00", "message": "别忘了完成今日学习目标！"},
            {"id": 3, "type": "review", "time": "21:00", "message": "是时候复习错题了！"}
        ]

    return [
        {"id": r['id'], "type": r['type'], "time": r['trigger_time'], "message": r['message_template']}
        for r in results
    ]


@router.post("")
async def create_reminder(type: str, time: str, message: str):
    """创建提醒"""
    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    user_id = user['id'] if user else 1

    db.execute(
        """INSERT INTO reminder_rules (user_id, type, trigger_time, message_template)
           VALUES (%s, %s, %s, %s)""",
        (user_id, type, time, message)
    )

    return {"message": "提醒创建成功"}


@router.delete("/{id}")
async def delete_reminder(id: int):
    """删除提醒"""
    db.execute("UPDATE reminder_rules SET enabled = 0 WHERE id = %s", (id,))
    return {"message": "提醒已删除"}
