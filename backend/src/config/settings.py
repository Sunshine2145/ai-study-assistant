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


class FeishuConfig(BaseModel):
    app_id: str = os.getenv("FEISHU_APP_ID", "")
    app_secret: str = os.getenv("FEISHU_APP_SECRET", "")
    bot_name: str = "AI伴学助手"
    verification_token: str = os.getenv("FEISHU_VERIFICATION_TOKEN", "")


class DatabaseConfig(BaseModel):
    path: str = os.getenv("DATABASE_PATH", "./database/questions.db")


class MySQLDatabaseConfig(BaseModel):
    host: str = os.getenv("MYSQL_HOST", "192.168.101.2")
    port: int = int(os.getenv("MYSQL_PORT", "3306"))
    database: str = os.getenv("MYSQL_DATABASE", "ai_study_assistant")
    user: str = os.getenv("MYSQL_USER", "ai_data")
    password: str = os.getenv("MYSQL_PASSWORD", "Xdzhzl2024")


class AIConfig(BaseModel):
    api_key: str = os.getenv("MINIMAX_API_KEY", "")
    model: str = "MiniMax-M2.5-highspeed"
    base_url: str = "https://api.minimaxi.com/v1"


class DeepSeekConfig(BaseModel):
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"


class ReminderConfig(BaseModel):
    default_times: List[str] = ["09:00", "20:00"]


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    feishu: FeishuConfig = FeishuConfig()
    database: DatabaseConfig = DatabaseConfig()
    mysql: MySQLDatabaseConfig = MySQLDatabaseConfig()
    ai: AIConfig = AIConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    reminder: ReminderConfig = ReminderConfig()
    db_type: str = os.getenv("DB_TYPE", "sqlite")


settings = Settings()


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_database_path() -> Path:
    db_path = Path(settings.database.path)
    if not db_path.is_absolute():
        db_path = get_project_root() / db_path
    return db_path
