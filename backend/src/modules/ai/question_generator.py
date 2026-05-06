# AI Study Assistant - Question Generator Service

import aiohttp
from loguru import logger


class QuestionGenerator:
    """Service for generating practice questions using AI"""

    PROMPT_TEMPLATE = """你是一个习题生成专家。请基于以下知识点，生成{count}道练习题。

知识点：{knowledge}

要求：
1. 题型包括：单选题、多选题、判断题
2. 难度适中，符合系统架构师考试风格
3. 每道题必须有详细解析
4. 覆盖核心概念和常见考点

返回格式（JSON数组）：
[
  {{
    "type": "single/multi/judge",
    "content": "题目内容",
    "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}},
    "answer": "B",
    "analysis": "详细解析"
  }}
]
"""

    def __init__(self, api_key: str, model: str = "MiniMax-M2.7"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.minimaxi.com/v1"

    async def generate(self, knowledge: str, count: int = 5) -> list:
        """Generate practice questions"""
        prompt = self.PROMPT_TEMPLATE.format(knowledge=knowledge, count=count)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        return self._parse_questions(content)
                    else:
                        error = await response.text()
                        logger.error(f"AI API error: {error}")
                        return []
        except Exception as e:
            logger.error(f"Question generator error: {e}")
            return []

    def _parse_questions(self, content: str) -> list:
        """Parse questions from AI response"""
        import re
        import json

        try:
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return []
        except Exception as e:
            logger.error(f"Question parsing error: {e}")
            return []
