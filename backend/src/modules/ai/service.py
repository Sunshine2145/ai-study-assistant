# AI Study Assistant - AI Service Module

from typing import Optional
from loguru import logger

from src.modules.ai.feynman import FeynmanService
from src.modules.ai.socratic import SocraticService
from src.modules.ai.pdf_parser import PDFParser
from src.modules.ai.question_generator import QuestionGenerator
from src.config.settings import settings


class AIService:
    """Central AI service coordinating all AI operations"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ai.api_key
        self.model = model or "MiniMax-M2.7"
        self.base_url = settings.ai.base_url
        self.feynman = FeynmanService(self.api_key, self.model)
        self.socratic = SocraticService(self.api_key, self.model)
        self.pdf_parser = PDFParser(self.api_key, self.model)
        self.question_generator = QuestionGenerator(self.api_key, self.model)

    async def generate_feynman_explanation(self, knowledge_code: str, knowledge_name: str) -> Optional[str]:
        """Generate Feynman explanation for a knowledge point using AI"""
        try:
            result = await self.feynman.explain(knowledge_name, "")
            return result
        except Exception as e:
            logger.error(f"Failed to generate Feynman explanation: {e}")
            return None

    async def feynman_explain(self, title: str, content: str) -> str:
        """Generate Feynman-style explanation"""
        logger.info(f"Generating Feynman explanation for: {title}")
        return await self.feynman.explain(title, content)

    async def socratic_question(
        self, knowledge: str, last_question: str, user_answer: str
    ) -> str:
        """Generate Socratic follow-up question"""
        logger.info("Generating Socratic question")
        return self.socratic.analyze(knowledge, user_answer)

    async def parse_pdf(self, text: str) -> list:
        """Parse questions from PDF text"""
        logger.info("Parsing PDF content")
        return await self.pdf_parser.parse(text)

    async def generate_questions(
        self, knowledge: str, count: int = 5
    ) -> list:
        """Generate practice questions based on knowledge point"""
        logger.info(f"Generating {count} questions for: {knowledge}")
        return await self.question_generator.generate(knowledge, count)
