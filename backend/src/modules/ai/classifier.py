# AI Study Assistant - Document Classifier

import aiohttp
import json
from loguru import logger

from src.config.settings import settings


class DocumentClassifier:
    """AI-powered document classifier"""

    PROMPT_TEMPLATE = """你是一个文档分类专家。请分析以下文档内容，判断它属于哪种类型：

文档内容（前2000字）：
{text}

请用JSON格式返回分类结果：
{{
    "classification": "knowledge_points 或 practice_questions 或 mixed 或 other",
    "confidence": 0.0-1.0的置信度,
    "reasoning": "分类理由"
}}

分类标准：
- knowledge_points: 知识点讲解、概念解释、理论说明
- practice_questions: 练习题、考试题、选择题、判断题
- mixed: 既包含知识点又包含题目
- other: 其他类型文档"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ai.api_key
        self.model = model or settings.ai.model
        self.base_url = settings.ai.base_url

    async def classify(self, text: str) -> dict:
        """Classify document content"""
        truncated = text[:2000]
        prompt = self.PROMPT_TEMPLATE.format(text=truncated)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        return self._parse_json(content)
        except Exception as e:
            logger.error(f"Document classification error: {e}")

        return {"classification": "other", "confidence": 0.5, "reasoning": "分类失败"}

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                return json.loads(text[start:end])
            except (ValueError, json.JSONDecodeError):
                return {"classification": "other", "confidence": 0.5, "reasoning": "解析失败"}
