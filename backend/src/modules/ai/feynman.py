# AI Study Assistant - Feynman Learning Service

import aiohttp
import json
from loguru import logger


class FeynmanService:
    """Service for generating Feynman-style explanations"""

    PROMPT_TEMPLATE = """你是AI学习助手，擅长用费曼学习法讲解知识点。
费曼学习法的核心是：用最简单的话把概念讲清楚，让8岁小孩都能听懂。

请用费曼学习法讲解以下知识点：

---
主题：{title}
内容：{content}
---

讲解要求：
1. 先用一个生活化的类比引入（用常见的场景解释）
2. 解释核心概念（不超3句话）
3. 举1-2个生活中的例子
4. 用"如果...会怎样"引导思考

格式要求：
- 用emoji增强可读性
- 段落清晰，逻辑递进
"""

    def __init__(self, api_key: str, model: str = "MiniMax-M2.7"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.minimaxi.com/v1"

    async def explain(self, title: str, content: str) -> str:
        """Generate Feynman-style explanation for a knowledge point"""
        prompt = self.PROMPT_TEMPLATE.format(title=title, content=content)

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
                        return result["choices"][0]["message"]["content"]
                    else:
                        error = await response.text()
                        logger.error(f"AI API error: {error}")
                        return f"抱歉，生成讲解时出现错误：{error}"
        except Exception as e:
            logger.error(f"Feynman service error: {e}")
            return f"抱歉，服务出现问题：{str(e)}"
