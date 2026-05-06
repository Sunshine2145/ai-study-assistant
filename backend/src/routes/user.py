# AI Study Assistant - User Routes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.database.db import db

router = APIRouter(prefix="/api/user", tags=["用户"])


class UserResponse(BaseModel):
    id: int
    nickname: str
    level: int
    score: int
    streak: int


@router.get("/current")
async def get_current_user():
    """获取当前用户信息（默认第一个用户）"""
    result = db.fetch_one(
        "SELECT id, nickname, level, score, streak FROM users LIMIT 1"
    )
    if not result:
        # 创建默认用户
        db.execute(
            "INSERT INTO users (nickname, feishu_openid) VALUES (?, ?)",
            ("谭晓磊", "default_user")
        )
        return {"id": 1, "nickname": "谭晓磊", "level": 1, "score": 0, "streak": 0}

    return {
        "id": result[0],
        "nickname": result[1] or "学员",
        "level": result[2] or 1,
        "score": result[3] or 0,
        "streak": result[4] or 0
    }


@router.get("/{user_id}")
async def get_user(user_id: int):
    """获取指定用户信息"""
    result = db.fetch_one(
        "SELECT id, nickname, level, score, streak FROM users WHERE id = ?",
        (user_id,)
    )
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "id": result[0],
        "nickname": result[1] or "学员",
        "level": result[2] or 1,
        "score": result[3] or 0,
        "streak": result[4] or 0
    }


@router.put("/{user_id}")
async def update_user(user_id: int, nickname: Optional[str] = None):
    """更新用户信息"""
    if nickname:
        db.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
    return {"message": "更新成功"}