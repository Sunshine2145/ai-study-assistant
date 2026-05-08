# AI Study Assistant - Knowledge Extractor

import aiohttp
import json
from loguru import logger

from src.config.settings import settings


class KnowledgeExtractor:
    """AI-powered knowledge point extractor from documents"""

    PROMPT_TEMPLATE = """你是知识提取专家。请从以下文档内容中提取结构化的知识点信息。

文档内容：
{text}

请用JSON数组格式返回提取的知识点列表：
[
    {{
        "code": "知识点编码（如1.2.3）",
        "name": "知识点名称",
        "chapter": "所属章节",
        "stage": "所属阶段",
        "content": "知识点详细内容",
        "summary": "简短摘要",
        "key_concepts": ["关键概念1", "关键概念2"]
    }}
]

如果无法提取有效的知识点，请返回空数组 []"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ai.api_key
        self.model = model or settings.ai.model
        self.base_url = settings.ai.base_url

    async def extract(self, text: str) -> list:
        """Extract knowledge points from document text"""
        chunks = self._split_text(text, 4000)
        all_knowledge = []

        for chunk in chunks:
            prompt = self.PROMPT_TEMPLATE.format(text=chunk)
            try:
                result = await self._call_api(prompt)
                parsed = self._parse_json_array(result)
                if parsed:
                    all_knowledge.extend(parsed)
            except Exception as e:
                logger.error(f"Knowledge extraction error: {e}")

        return all_knowledge

    def _split_text(self, text: str, max_length: int) -> list:
        if len(text) <= max_length:
            return [text]
        chunks = []
        while text:
            if len(text) <= max_length:
                chunks.append(text)
                break
            split_point = text.rfind("\n", 0, max_length)
            if split_point == -1:
                split_point = max_length
            chunks.append(text[:split_point])
            text = text[split_point:].lstrip("\n")
        return chunks

    async def _call_api(self, prompt: str) -> str:
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
                    return result["choices"][0]["message"]["content"]
                return ""

    def _parse_json_array(self, text: str) -> list:
        if not text:
            return []
        try:
            result = json.loads(text)
            return result if isinstance(result, list) else []
        except json.JSONDecodeError:
            pass
        try:
            start = text.index("[")
            end = text.rindex("]") + 1
            result = json.loads(text[start:end])
            return result if isinstance(result, list) else []
        except (ValueError, json.JSONDecodeError):
            return []
