# AI Study Assistant - Configuration Settings

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class AppConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5001


class MySQLConfig(BaseModel):
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "Xdzhzl2024")
    host: str = os.getenv("MYSQL_HOST", "10.42.200.104")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    database: str = os.getenv("MYSQL_DATABASE", "ai_study")
    charset: str = "utf8mb4"


class FeishuConfig(BaseModel):
    app_id: str = os.getenv("FEISHU_APP_ID", "")
    app_secret: str = os.getenv("FEISHU_APP_SECRET", "")
    bot_name: str = "AI伴学助手"
    verification_token: str = os.getenv("FEISHU_VERIFICATION_TOKEN", "")


class DatabaseConfig(BaseModel):
    path: str = os.getenv("DATABASE_PATH", "./database/questions.db")


class AIConfig(BaseModel):
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"


class DeepSeekConfig(BaseModel):
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"


class ReminderConfig(BaseModel):
    default_times: List[str] = ["09:00", "20:00"]


class JWTConfig(BaseModel):
    secret: str = os.getenv("JWT_SECRET", "ai-study-assistant-secret-key-change-in-production")
    algorithm: str = "HS256"
    expire_minutes: int = 1440  # 24 hours


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    mysql: MySQLConfig = MySQLConfig()
    feishu: FeishuConfig = FeishuConfig()
    database: DatabaseConfig = DatabaseConfig()
    ai: AIConfig = AIConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    reminder: ReminderConfig = ReminderConfig()
    jwt: JWTConfig = JWTConfig()


settings = Settings()


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_database_path() -> Path:
    db_path = Path(settings.database.path)
    if not db_path.is_absolute():
        db_path = get_project_root() / db_path
    return db_path
