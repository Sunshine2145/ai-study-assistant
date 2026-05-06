# AI Study Assistant - Feishu Bot Module

from fastapi import APIRouter, Request, HTTPException
from loguru import logger
import json

from src.config.settings import settings
from src.modules.feishu.handlers.command import CommandHandler
from src.modules.feishu.handlers.chat import ChatHandler
from src.modules.feishu.handlers.schedule import ScheduleHandler


router = APIRouter()


class FeishuBot:
    """Main Feishu bot handler"""

    def __init__(self):
        self.command_handler = CommandHandler()
        self.chat_handler = ChatHandler()
        self.schedule_handler = ScheduleHandler()

    async def handle_message(self, message: dict):
        """Route incoming messages to appropriate handlers"""
        msg_type = message.get("msg_type", "")
        content = message.get("content", "")

        # Handle commands
        if content.startswith("/"):
            return await self.command_handler.handle(content)

        # Handle regular chat
        return await self.chat_handler.handle(content)


bot = FeishuBot()


@router.post("/webhook")
async def handle_feishu_webhook(request: Request):
    """Handle incoming Feishu webhook events"""
    try:
        body = await request.json()
        logger.info(f"Received Feishu webhook: {body}")

        # Handle URL verification
        if body.get("type") == "url_verification":
            challenge = body.get("challenge", "")
            return {"challenge": challenge}

        # Handle events
        if body.get("type") == "event":
            event = body.get("event", {})
            msg_type = event.get("msg_type", "")
            content = event.get("content", {})

            if msg_type == "text":
                text = content.get("text", "")
                result = await bot.handle_message({"msg_type": msg_type, "content": text})
                return {"status": "ok", "data": result}

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(recipient_id: str, content: str):
    """Send message to user via Feishu"""
    try:
        from src.modules.feishu.feishu_client import FeishuClient
        client = FeishuClient()
        return await client.send_message(recipient_id, content)
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
