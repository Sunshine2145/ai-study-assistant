# AI Study Assistant - Configuration Settings

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class AppConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8081


class FeishuConfig(BaseModel):
    app_id: str = os.getenv("FEISHU_APP_ID", "")
    app_secret: str = os.getenv("FEISHU_APP_SECRET", "")
    bot_name: str = "AI伴学助手"
    verification_token: str = os.getenv("FEISHU_VERIFICATION_TOKEN", "")


class DatabaseConfig(BaseModel):
    path: str = os.getenv("DATABASE_PATH", "./database/questions.db")


class AIConfig(BaseModel):
    api_key: str = os.getenv("MINIMAX_API_KEY", "")
    model: str = "MiniMax-M2.7"
    base_url: str = "https://api.minimaxi.com/v1"


class DeepSeekConfig(BaseModel):
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"


class ReminderConfig(BaseModel):
    default_times: List[str] = ["09:00", "20:00"]


class Settings(BaseModel):
    app: AppConfig = AppConfig()
    feishu: FeishuConfig = FeishuConfig()
    database: DatabaseConfig = DatabaseConfig()
    ai: AIConfig = AIConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    reminder: ReminderConfig = ReminderConfig()


settings = Settings()


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_database_path() -> Path:
    db_path = Path(settings.database.path)
    if not db_path.is_absolute():
        db_path = get_project_root() / db_path
    return db_path
