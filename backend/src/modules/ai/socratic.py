# AI Study Assistant - Socratic Questioning Service (AI-Powered)

import aiohttp
import json
from loguru import logger

from src.config.settings import settings


class SocraticService:
    """AI-powered Socratic questioning service using MiniMax API"""

    MAX_QUESTIONS = 5

    LEVELS = [
        "事实性问题（是什么）",
        "理解性问题（为什么）",
        "应用性问题（怎么用）",
        "分析性问题（与什么相关）",
        "评价性问题（你怎么看）",
    ]

    QUESTION_PROMPT_TEMPLATE = """你是AI学习助手，擅长用苏格拉底提问法引导学生思考。
苏格拉底法的核心：不直接给答案，通过连续追问让学生自己发现答案。

当前知识点：{knowledge}

这是第{question_number}个问题，难度级别：{level}

{history_context}

请根据以上信息，生成一个苏格拉底式的引导问题。

要求：
1. 不要直接给出答案或解释
2. 问题要引导学生深入思考
3. 根据难度级别选择合适的问题层次
4. 问题要具体、清晰，便于学生回答

请用JSON格式返回：
{{"question": "你生成的问题"}}"""

    ANALYSIS_PROMPT_TEMPLATE = """你是AI学习助手，擅长用苏格拉底提问法引导学生思考。

当前知识点：{knowledge}
AI的问题：{question}
学生的回答：{answer}

请分析学生的回答，评估其理解程度。

评估标准：
- 优秀(Excellent): 完全正确且理解深入 → 掌握度+25%
- 良好(Good): 正确但理解较浅 → 掌握度+15%
- 部分正确(Partial): 部分理解 → 掌握度+8%
- 较差(Poor): 方向对但细节错 → 掌握度+5%
- 错误(Wrong): 完全错误 → 掌握度+0%

请用JSON格式返回：
{{
    "answer_quality": 0-100的分数,
    "mastery_delta": 掌握度增加百分比(25/15/8/5/0),
    "grade": "excellent/good/partial/poor/wrong",
    "feedback": "针对学生回答的反馈（肯定或引导纠正）",
    "follow_up_question": "下一个引导问题（如果有）",
    "is_understanding_correct": true/false,
    "needs_clarification": true/false
}}"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ai.api_key
        self.model = model or settings.ai.model
        self.base_url = settings.ai.base_url

    async def generate_question(
        self, knowledge_name: str, knowledge_code: str, level: int, history: list = None
    ) -> dict:
        """Generate a Socratic question at the specified difficulty level"""
        level = min(level, len(self.LEVELS) - 1)
        question_number = (len(history) // 2 + 1) if history else 1

        history_context = ""
        if history:
            history_lines = []
            for i in range(0, len(history) - 1, 2):
                if i + 1 < len(history):
                    history_lines.append(f"Q: {history[i]}")
                    history_lines.append(f"A: {history[i + 1]}")
            if history_lines:
                history_context = "之前的问答记录：\n" + "\n".join(history_lines[-6:])

        prompt = self.QUESTION_PROMPT_TEMPLATE.format(
            knowledge=f"{knowledge_name}（{knowledge_code}）",
            question_number=question_number,
            level=self.LEVELS[level],
            history_context=history_context or "这是第一个问题。",
        )

        try:
            result = await self._call_api(prompt)
            parsed = self._parse_json_response(result)
            if parsed and "question" in parsed:
                return {
                    "question": parsed["question"],
                    "level": level,
                    "question_number": question_number,
                }
        except Exception as e:
            logger.error(f"Generate question error: {e}")

        fallback_questions = [
            f"你能用自己的话描述一下{knowledge_name}是什么吗？",
            f"为什么{knowledge_name}在系统架构中很重要？",
            f"你能举一个{knowledge_name}在实际项目中应用的例子吗？",
            f"{knowledge_name}与其他概念有什么关联？",
            f"你认为{knowledge_name}的关键要点是什么？",
        ]
        idx = min(level, len(fallback_questions) - 1)
        return {
            "question": fallback_questions[idx],
            "level": level,
            "question_number": question_number,
        }

    async def analyze_answer(
        self, knowledge_name: str, question: str, user_answer: str, history: list = None
    ) -> dict:
        """Analyze user's answer and return feedback with mastery delta"""
        prompt = self.ANALYSIS_PROMPT_TEMPLATE.format(
            knowledge=knowledge_name,
            question=question,
            answer=user_answer,
        )

        try:
            result = await self._call_api(prompt)
            parsed = self._parse_json_response(result)
            if parsed:
                return {
                    "answer_quality": parsed.get("answer_quality", 50),
                    "mastery_delta": parsed.get("mastery_delta", 5),
                    "grade": parsed.get("grade", "partial"),
                    "feedback": parsed.get("feedback", "收到你的回答。"),
                    "follow_up_question": parsed.get("follow_up_question", ""),
                    "is_understanding_correct": parsed.get("is_understanding_correct", False),
                    "needs_clarification": parsed.get("needs_clarification", False),
                }
        except Exception as e:
            logger.error(f"Analyze answer error: {e}")

        answer_len = len(user_answer)
        if answer_len > 50:
            delta, grade = 15, "good"
            feedback = "回答内容较多，理解基本正确。"
        elif answer_len > 20:
            delta, grade = 8, "partial"
            feedback = "有一定理解，但可以更深入。"
        else:
            delta, grade = 5, "poor"
            feedback = "回答较简短，请尝试更详细地解释。"

        return {
            "answer_quality": delta * 4,
            "mastery_delta": delta,
            "grade": grade,
            "feedback": feedback,
            "follow_up_question": f"关于{knowledge_name}，你能再深入解释一下吗？",
            "is_understanding_correct": delta >= 15,
            "needs_clarification": delta < 8,
        }

    async def _call_api(self, prompt: str) -> str:
        """Call MiniMax API"""
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
                else:
                    error = await response.text()
                    logger.error(f"AI API error: {error}")
                    return ""

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from AI response with fallback"""
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError):
            pass
        try:
            start = text.index("{")
            brace_count = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return json.loads(text[start : i + 1])
        except (ValueError, json.JSONDecodeError):
            pass
        return None
