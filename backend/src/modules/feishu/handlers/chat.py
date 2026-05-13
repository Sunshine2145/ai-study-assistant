# AI Study Assistant - Chat Handler

from loguru import logger

from src.config.settings import settings
from src.modules.ai.service import AIService
from src.database.db import db


class ChatHandler:
    """Handler for regular chat messages"""

    def __init__(self):
        self.ai_service = AIService(
            api_key=settings.ai.api_key,
            model=settings.ai.model
        )

    async def handle(self, message: str, user_id: int = 1) -> str:
        """Process chat message and return AI response"""
        logger.info(f"Processing chat message: {message}")

        if message.startswith("学习") or message.startswith("讲解"):
            topic = message.replace("学习", "").replace("讲解", "").strip()
            return await self._handle_learning(topic, user_id)

        if message.startswith("练习") or message.startswith("做题"):
            topic = message.replace("练习", "").replace("做题", "").strip()
            return await self._handle_practice(topic, user_id)

        return await self._handle_general_learning(message, user_id)

    async def _handle_learning(self, topic: str, user_id: int) -> str:
        kp = db.fetch_one(
            "SELECT code, name FROM knowledge_points WHERE name LIKE %s OR code = %s",
            (f"%{topic}%", topic)
        )

        if kp:
            return await self.ai_service.feynman_explain(kp['name'], kp['name'])
        else:
            return await self.ai_service.feynman_explain(topic, topic)

    async def _handle_practice(self, topic: str, user_id: int) -> str:
        questions = await self.ai_service.generate_questions(topic, 5)
        if questions:
            return self._format_questions(questions)
        else:
            return "抱歉，暂无相关练习题。试试其他知识点~"

    async def _handle_general_learning(self, message: str, user_id: int) -> str:
        return await self.ai_service.feynman_explain(message, message)

    def _format_questions(self, questions: list) -> str:
        formatted = ["📝 **练习题**", ""]

        for i, q in enumerate(questions, 1):
            q_type = {"single": "单选题", "multi": "多选题", "judge": "判断题"}.get(
                q.get("type", "single"), "题"
            )
            formatted.append(f"**{i}. {q_type}**")
            formatted.append(q.get("content", ""))
            formatted.append("")

            options = q.get("options", {})
            if options:
                for opt, val in options.items():
                    formatted.append(f"  {opt}. {val}")
                formatted.append("")

        return "\n".join(formatted)
