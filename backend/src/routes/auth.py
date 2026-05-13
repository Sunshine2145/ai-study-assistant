# AI Study Assistant - Auth Routes

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import hashlib
import random
import string
import json
import jwt
from datetime import datetime, timedelta

from src.database.db import db
from src.config.settings import settings

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


# Verification codes (in-memory; use Redis in production)
verification_codes = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt.expire_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt.secret, algorithm=settings.jwt.algorithm)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.jwt.secret, algorithms=[settings.jwt.algorithm])
        return payload
    except jwt.PyJWTError:
        return None


def generate_verification_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def get_current_user_id() -> int:
    """Get the default/first user ID for endpoints that don't require auth"""
    user = db.fetch_one("SELECT id FROM users LIMIT 1")
    return user['id'] if user else 1


@router.post("/register")
async def register(request: RegisterRequest):
    existing = db.fetch_one(
        "SELECT id FROM users WHERE username = %s",
        (request.username,)
    )
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    password_hash = hash_password(request.password)
    nickname = request.nickname or request.username

    cursor = db.execute(
        """INSERT INTO users (username, password_hash, nickname, email, role, permissions, status)
           VALUES (%s, %s, %s, %s, 'user', %s, 'active')""",
        (request.username, password_hash, nickname, request.email or "",
         json.dumps(["map", "learn", "practice", "wrong", "report", "upload", "ai-qa"], ensure_ascii=False))
    )

    user_id = cursor.lastrowid

    default_modules = ["map", "learn", "practice", "wrong", "report", "upload", "ai-qa"]
    for module in default_modules:
        db.execute(
            "INSERT INTO user_permissions (user_id, module) VALUES (%s, %s)",
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
    password_hash = hash_password(request.password)

    user = db.fetch_one(
        """SELECT id, username, password_hash, nickname, role, permissions, status
           FROM users WHERE username = %s""",
        (request.username,)
    )

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user['password_hash'] != password_hash and user['password_hash'] != request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user['status'] == "banned":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = generate_token(user['id'], user['username'])

    perms = json.loads(user['permissions']) if user['permissions'] else []

    return {
        "user_id": user['id'],
        "username": user['username'],
        "nickname": user['nickname'],
        "role": user['role'],
        "permissions": perms,
        "token": token
    }


@router.get("/me")
async def get_current_user():
    user = db.fetch_one(
        "SELECT id, nickname, level, score, streak FROM users LIMIT 1"
    )
    if not user:
        return {"id": 1, "nickname": "谭晓磊", "level": 1, "score": 0, "streak": 0}

    return {
        "id": user['id'],
        "nickname": user['nickname'] or "学员",
        "level": user['level'] or 1,
        "score": user['score'] or 0,
        "streak": user['streak'] or 0
    }


@router.get("/current")
async def get_current_user_full():
    user = db.fetch_one(
        "SELECT id, username, nickname, email, role, permissions, status, score, streak FROM users LIMIT 1"
    )
    if not user:
        return {"id": 1, "username": "tanxiaolei", "nickname": "谭晓磊", "email": "",
                "role": "admin", "permissions": [], "status": "active", "score": 0, "streak": 0}

    perms = json.loads(user['permissions']) if user['permissions'] else []

    return {
        "id": user['id'],
        "username": user['username'],
        "nickname": user['nickname'] or user['username'],
        "email": user['email'] or "",
        "role": user['role'] or "user",
        "permissions": perms,
        "status": user['status'] or "active",
        "score": user['score'] or 0,
        "streak": user['streak'] or 0
    }


@router.post("/send-code")
async def send_verification_code(request: SendCodeRequest):
    user = db.fetch_one(
        "SELECT id FROM users WHERE username = %s",
        (request.username,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    code = generate_verification_code()

    verification_codes[request.username] = {
        "code": code,
        "expires": datetime.now() + timedelta(minutes=5)
    }

    print(f"验证码: {code} (仅开发环境显示)")

    return {
        "success": True,
        "message": "验证码已发送"
    }


@router.post("/login-code")
async def login_with_code(request: LoginCodeRequest):
    stored = verification_codes.get(request.username)
    if not stored:
        raise HTTPException(status_code=400, detail="请先获取验证码")

    if datetime.now() > stored["expires"]:
        del verification_codes[request.username]
        raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")

    if stored["code"] != request.code:
        raise HTTPException(status_code=400, detail="验证码错误")

    del verification_codes[request.username]

    user = db.fetch_one(
        """SELECT id, username, nickname, role, permissions, status
           FROM users WHERE username = %s""",
        (request.username,)
    )

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user['status'] == "banned":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = generate_token(user['id'], user['username'])

    perms = json.loads(user['permissions']) if user['permissions'] else []

    return {
        "user_id": user['id'],
        "username": user['username'],
        "nickname": user['nickname'],
        "role": user['role'],
        "permissions": perms,
        "token": token
    }
