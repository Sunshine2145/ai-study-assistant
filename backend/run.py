# AI Study Assistant - Backend Entry Point

import uvicorn
from loguru import logger

from src.config.settings import settings
from src.modules.feishu.bot import FeishuBot
from src.database.db import init_database, create_database_if_not_exists


def main():
    logger.info("Starting AI伴学系统...")

    # Create database if not exists
    create_database_if_not_exists()

    # Initialize database tables
    init_database()

    # Initialize Feishu bot
    bot = FeishuBot()

    # Start server
    logger.info(f"Server starting on {settings.app.host}:{settings.app.port}")
    uvicorn.run(
        "src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )


if __name__ == "__main__":
    main()
