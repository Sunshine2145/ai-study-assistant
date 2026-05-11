# AI Study Assistant - Auth Routes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
import random
import string
from datetime import datetime, timedelta

from src.database.db import db

router = APIRouter(prefix="/api/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginCodeRequest(BaseModel):
    username: str
    code: str


class SendCodeRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    user_id: int
    username: str
    nickname: str
    role: str
    permissions: Optional[list] = None
    token: str


# 验证码存储 (生产环境应使用Redis)
verification_codes = {}


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id: int, username: str) -> str:
    """Generate simple token"""
    return hashlib.sha256(f"{user_id}:{username}:{datetime.now()}".encode()).hexdigest()


def generate_verification_code(length: int = 6) -> str:
    """Generate numeric verification code"""
    return ''.join(random.choices(string.digits, k=length))


@router.post("/register")
async def register(request: RegisterRequest):
    """用户注册"""
    # Check if username already exists
    existing = db.fetch_one(
        "SELECT id FROM users WHERE username = ?",
        (request.username,)
    )
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # Hash password
    password_hash = hash_password(request.password)

    # Create user
    nickname = request.nickname or request.username
    cursor = db.execute(
        """INSERT INTO users (username, password_hash, nickname, email, role, permissions, status)
           VALUES (?, ?, ?, ?, 'user', '["map","learn","socratic","practice","wrong","report","upload","question-bank","ai-qa"]', 'active')""",
        (request.username, password_hash, nickname, request.email or "")
    )

    user_id = cursor.lastrowid

    # Create default permissions (匹配 PRD v1.6 模块列表)
    default_modules = ["map", "learn", "socratic", "practice", "wrong", "report", "upload", "question-bank", "ai-qa"]
    for module in default_modules:
        db.execute(
            "INSERT INTO user_permissions (user_id, module) VALUES (?, ?)",
            (user_id, module)
        )

    token = generate_token(user_id, request.username)

    return {
        "user_id": user_id,
        "username": request.username,
        "nickname": nickname,
        "role": "user",
        "token": token
    }


@router.post("/login")
async def login(request: LoginRequest):
    """用户登录"""
    # Hash password
    password_hash = hash_password(request.password)

    # Find user
    user = db.fetch_one(
        """SELECT id, username, password_hash, nickname, role, permissions, status
           FROM users WHERE username = ?""",
        (request.username,)
    )

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    user_id, username, stored_hash, nickname, role, permissions, status = user

    # Check password (also allow legacy feishu_openid login)
    if stored_hash != password_hash and user[2] != request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Check status
    if status == "banned":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = generate_token(user_id, username)

    # Parse permissions
    import json
    perms = json.loads(permissions) if permissions else []

    return {
        "user_id": user_id,
        "username": username,
        "nickname": nickname,
        "role": role,
        "permissions": perms,
        "token": token
    }


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    # 先尝试从数据库获取第一个用户
    user = db.fetch_one(
        "SELECT id, nickname, level, score, streak FROM users LIMIT 1"
    )
    if not user:
        return {"id": 1, "nickname": "谭晓磊", "level": 1, "score": 0, "streak": 0}

    return {
        "id": user[0],
        "nickname": user[1] or "学员",
        "level": user[2] or 1,
        "score": user[3] or 0,
        "streak": user[4] or 0
    }


@router.get("/current")
async def get_current_user_full():
    """获取当前用户完整信息"""
    user = db.fetch_one(
        "SELECT id, username, nickname, email, role, permissions, status, score, streak FROM users LIMIT 1"
    )
    if not user:
        return {"id": 1, "username": "tanxiaolei", "nickname": "谭晓磊", "email": "", "role": "admin", "permissions": [], "status": "active", "score": 0, "streak": 0}

    import json
    perms = json.loads(user[5]) if user[5] else []

    return {
        "id": user[0],
        "username": user[1],
        "nickname": user[2] or user[1],
        "email": user[3] or "",
        "role": user[4] or "user",
        "permissions": perms,
        "status": user[6] or "active",
        "score": user[7] or 0,
        "streak": user[8] or 0
    }


@router.post("/send-code")
async def send_verification_code(request: SendCodeRequest):
    """发送验证码"""
    # 检查用户是否存在
    user = db.fetch_one(
        "SELECT id FROM users WHERE username = ?",
        (request.username,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成6位验证码
    code = generate_verification_code()

    # 存储验证码，设置5分钟过期
    verification_codes[request.username] = {
        "code": code,
        "expires": datetime.now() + timedelta(minutes=5)
    }

    # 实际生产环境应该发送短信，这里只是模拟
    print(f"验证码: {code} (仅开发环境显示)")

    return {
        "success": True,
        "message": "验证码已发送"
    }


@router.post("/login-code")
async def login_with_code(request: LoginCodeRequest):
    """验证码登录"""
    # 检查验证码
    stored = verification_codes.get(request.username)
    if not stored:
        raise HTTPException(status_code=400, detail="请先获取验证码")

    # 检查是否过期
    if datetime.now() > stored["expires"]:
        del verification_codes[request.username]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    # 验证验证码
    if stored["code"] != request.code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 验证成功，删除验证码
    del verification_codes[request.username]

    # 获取用户信息
    user = db.fetch_one(
        """SELECT id, username, nickname, role, permissions, status
           FROM users WHERE username = ?""",
        (request.username,)
    )

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id, username, nickname, role, permissions, status = user

    # 检查状态
    if status == "banned":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = generate_token(user_id, username)

    import json
    perms = json.loads(permissions) if permissions else []

    return {
        "user_id": user_id,
        "username": username,
        "nickname": nickname,
        "role": role,
        "permissions": perms,
        "token": token
    }