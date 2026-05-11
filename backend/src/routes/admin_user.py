# AI Study Assistant - User Management Routes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import hashlib

from src.database.db import db

router = APIRouter(prefix="/api/admin/users", tags=["用户管理"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


PRD_MODULES = [
    "map",           # 学习地图
    "learn",         # 知识点讲解（费曼学习法）
    "socratic",      # AI帮测（苏格拉底提问）
    "practice",      # 题目练习
    "wrong",         # 错题本
    "report",        # 学习报告
    "upload",        # 题库上传
    "question-bank", # 题库管理
    "ai-qa",         # AI问答
]


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str
    status: str
    permissions: List[str]
    score: int
    streak: int


class UpdatePermissionsRequest(BaseModel):
    user_id: int
    permissions: List[str]


class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class CreateUserRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = "user"
    permissions: Optional[List[str]] = None


class ResetPasswordRequest(BaseModel):
    password: str


@router.get("/list")
async def get_user_list():
    """获取用户列表（管理员）"""
    users = db.fetch_all(
        """SELECT id, username, nickname, email, role, status, score, streak
           FROM users ORDER BY id DESC"""
    )

    result = []
    for u in users:
        user_id, username, nickname, email, role, status, score, streak = u

        # Get permissions
        perms = db.fetch_all(
            "SELECT module FROM user_permissions WHERE user_id = ?",
            (user_id,)
        )
        permissions = [p[0] for p in perms] if perms else []

        result.append({
            "id": user_id,
            "username": username,
            "nickname": nickname or username,
            "email": email or "",
            "role": role or "user",
            "status": status or "active",
            "permissions": permissions,
            "score": score or 0,
            "streak": streak or 0
        })

    return {"data": result}


@router.get("/{user_id}")
async def get_user(user_id: int):
    """获取指定用户信息"""
    user = db.fetch_one(
        """SELECT id, username, nickname, email, role, status, score, streak
           FROM users WHERE id = ?""",
        (user_id,)
    )

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Get permissions
    perms = db.fetch_all(
        "SELECT module FROM user_permissions WHERE user_id = ?",
        (user_id,)
    )
    permissions = [p[0] for p in perms] if perms else []

    return {
        "id": user[0],
        "username": user[1],
        "nickname": user[2] or user[1],
        "email": user[3] or "",
        "role": user[4] or "user",
        "status": user[5] or "active",
        "permissions": permissions,
        "score": user[6] or 0,
        "streak": user[7] or 0
    }


@router.put("/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest):
    """更新用户信息"""
    # Check if user exists
    existing = db.fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Build update query
    updates = []
    params = []

    if request.nickname:
        updates.append("nickname = ?")
        params.append(request.nickname)
    if request.email:
        updates.append("email = ?")
        params.append(request.email)
    if request.role:
        updates.append("role = ?")
        params.append(request.role)
    if request.status:
        updates.append("status = ?")
        params.append(request.status)

    if not updates:
        return {"message": "没有需要更新的内容"}

    params.append(user_id)
    db.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", tuple(params))

    return {"message": "用户信息更新成功"}


@router.put("/{user_id}/permissions")
async def update_user_permissions(user_id: int, request: UpdatePermissionsRequest):
    """更新用户权限"""
    # Check if user exists
    existing = db.fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Delete existing permissions
    db.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))

    # Insert new permissions
    for module in request.permissions:
        db.execute(
            "INSERT INTO user_permissions (user_id, module) VALUES (?, ?)",
            (user_id, module)
        )

    # Also update the JSON field
    db.execute(
        "UPDATE users SET permissions = ? WHERE id = ?",
        (json.dumps(request.permissions), user_id)
    )

    return {"message": "权限更新成功", "permissions": request.permissions}


@router.post("/{user_id}/ban")
async def ban_user(user_id: int):
    """禁用用户"""
    existing = db.fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.execute("UPDATE users SET status = 'banned' WHERE id = ?", (user_id,))
    return {"message": "用户已禁用"}


@router.post("/{user_id}/unban")
async def unban_user(user_id: int):
    """启用用户"""
    existing = db.fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
    return {"message": "用户已启用"}


@router.post("")
async def create_user(request: CreateUserRequest):
    """管理员手动添加用户"""
    # Check if username already exists
    existing = db.fetch_one(
        "SELECT id FROM users WHERE username = ?",
        (request.username,)
    )
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # Hash password
    password_hash = hash_password(request.password)

    # Determine permissions
    perms = request.permissions or PRD_MODULES

    # Create user
    nickname = request.nickname or request.username
    cursor = db.execute(
        """INSERT INTO users (username, password_hash, nickname, email, role, permissions, status)
           VALUES (?, ?, ?, ?, ?, ?, 'active')""",
        (request.username, password_hash, nickname, request.email or "", request.role, json.dumps(perms))
    )

    user_id = cursor.lastrowid

    # Create permission records
    for module in perms:
        db.execute(
            "INSERT INTO user_permissions (user_id, module) VALUES (?, ?)",
            (user_id, module)
        )

    return {
        "user_id": user_id,
        "username": request.username,
        "nickname": nickname,
        "email": request.email or "",
        "role": request.role or "user",
        "permissions": perms,
        "message": "用户创建成功"
    }


@router.post("/{user_id}/reset-password")
async def reset_user_password(user_id: int, request: ResetPasswordRequest):
    """管理员重置用户密码"""
    existing = db.fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    password_hash = hash_password(request.password)
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (password_hash, user_id)
    )

    return {"message": "密码重置成功"}