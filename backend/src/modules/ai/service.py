# AI Study Assistant - AI Service Module

from typing import Optional
from loguru import logger

from src.modules.ai.feynman import FeynmanService
from src.modules.ai.socratic import SocraticService
from src.modules.ai.pdf_parser import PDFParser
from src.modules.ai.question_generator import QuestionGenerator
from src.modules.ai.classifier import DocumentClassifier
from src.modules.ai.knowledge_extractor import KnowledgeExtractor
from src.modules.ai.question_extractor import QuestionExtractor
from src.config.settings import settings


class AIService:
    """Central AI service coordinating all AI operations"""

    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or settings.ai.api_key
        self.model = model or settings.ai.model
        self.base_url = base_url or settings.ai.base_url

        # Pass consistent api_key, model, and base_url to ALL sub-services
        self.feynman = FeynmanService(self.api_key, self.model, self.base_url)
        self.socratic = SocraticService(self.api_key, self.model)
        self.pdf_parser = PDFParser(self.api_key, self.model, self.base_url)
        self.question_generator = QuestionGenerator(self.api_key, self.model, self.base_url)
        self.classifier = DocumentClassifier(self.api_key, self.model)
        self.knowledge_extractor = KnowledgeExtractor(self.api_key, self.model)
        self.question_extractor = QuestionExtractor(self.api_key, self.model)

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

    async def socratic_generate_question(
        self, knowledge_name: str, knowledge_code: str, level: int, history: list = None
    ) -> dict:
        """Generate a Socratic question at the specified level"""
        logger.info(f"Generating Socratic question level={level} for {knowledge_code}")
        return await self.socratic.generate_question(knowledge_name, knowledge_code, level, history)

    async def socratic_analyze_answer(
        self, knowledge_name: str, question: str, user_answer: str, history: list = None
    ) -> dict:
        """Analyze user answer in Socratic mode"""
        logger.info("Analyzing Socratic answer")
        return await self.socratic.analyze_answer(knowledge_name, question, user_answer, history)

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

    async def classify_document(self, text: str) -> dict:
        """Classify document content type"""
        logger.info("Classifying document")
        return await self.classifier.classify(text)

    async def extract_knowledge(self, text: str) -> list:
        """Extract knowledge points from document"""
        logger.info("Extracting knowledge points")
        return await self.knowledge_extractor.extract(text)

    async def extract_questions_from_text(self, text: str) -> list:
        """Extract questions from document"""
        logger.info("Extracting questions from document")
        return await self.question_extractor.extract(text)
