# AI Study Assistant - Chat Routes

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from src.database.db import db
from src.modules.ai.feynman import FeynmanService
from src.modules.ai.socratic import SocraticService
from src.config.settings import settings

router = APIRouter(prefix="/api/chat", tags=["聊天"])


class ChatRequest(BaseModel):
    content: str
    knowledge_id: Optional[int] = None
    knowledge_code: Optional[str] = None


@router.post("")
async def send_message(request: ChatRequest):
    """处理用户聊天消息"""
    knowledge_id = request.knowledge_id
    knowledge_code = request.knowledge_code
    knowledge_name = None

    if knowledge_id:
        kp = db.fetch_one(
            "SELECT id, code, name FROM knowledge_points WHERE id = ?",
            (knowledge_id,)
        )
        if kp:
            knowledge_id, knowledge_code, knowledge_name = kp
    else:
        current = db.fetch_one(
            "SELECT id, code, name FROM knowledge_points WHERE status = 'unlocked' ORDER BY sort_order LIMIT 1"
        )
        if current:
            knowledge_id, knowledge_code, knowledge_name = current

    if not knowledge_id:
        return {
            "data": {
                "response": "您好！请先从学习地图选择一个知识点开始学习。",
                "socratic_hint": "请选择一个知识点开始学习",
                "knowledge_name": None
            }
        }

    if knowledge_name:
        user_lower = request.content.lower()
        teaching_keywords = ["讲解", "解释", "讲讲", "介绍一下", "什么是", "说说", "帮我学习", "开始学习", "讲", "教"]
        if any(kw in user_lower for kw in teaching_keywords):
            return await _generate_feynman_explanation(knowledge_id, knowledge_code, knowledge_name, request.content)

    return await _process_socratic_answer(knowledge_id, knowledge_code, knowledge_name, request.content)


async def _generate_feynman_explanation(knowledge_id: int, knowledge_code: str, knowledge_name: str, user_message: str):
    """Generate Feynman-style explanation using AI"""
    feynman = FeynmanService(settings.ai.api_key, "MiniMax-M2.7")

    try:
        explanation = await feynman.explain(knowledge_name, "")

        if explanation and not explanation.startswith("抱歉"):
            response = f"""📚 **费曼学习法讲解：{knowledge_name}**

{explanation}

---

💡 现在轮到你来练习了！请用一句话概括一下这个知识点的核心内容，这样可以帮助我了解你的理解程度。"""
        else:
            response = f"""📚 **关于 {knowledge_name}**

对不起，AI服务暂时不可用。请用自己的话简要描述一下这个概念：

**{knowledge_name}** 是关于什么的？它的主要特点是什么？

你可以试着用简单的语言解释，这样能帮助我了解你的理解程度。"""

        return {
            "data": {
                "response": response,
                "socratic_hint": f"正在学习：{knowledge_name}",
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "feynman"
            }
        }
    except Exception as e:
        logger.error(f"Feynman explanation error: {e}")
        return {
            "data": {
                "response": f"""📚 **关于 {knowledge_name}**

请试着用自己的话描述一下：

**{knowledge_name}** 是关于什么的？它有什么特点和作用？

用简单的语言解释可以帮助我了解你的理解程度。""",
                "socratic_hint": f"正在学习：{knowledge_name}",
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "feynman"
            }
        }


async def _process_socratic_answer(knowledge_id: int, knowledge_code: str, knowledge_name: str, user_message: str):
    """Process user's answer with Socratic questioning"""
    progress = db.fetch_one("""
        SELECT mastery_percentage, socratic_rounds
        FROM learning_progress
        WHERE knowledge_point_id = ?
    """, (knowledge_id,))

    current_mastery = progress[0] if progress else 0
    current_rounds = progress[1] if progress else 0

    socratic = SocraticService(api_key=settings.ai.api_key)
    analysis = socratic.analyze(knowledge_code, user_message)

    answer_quality = analysis.get("answer_quality", 50)
    new_rounds = current_rounds + 1

    if answer_quality >= 70:
        mastery_increase = 15
    elif answer_quality >= 50:
        mastery_increase = 10
    elif answer_quality >= 30:
        mastery_increase = 5
    else:
        mastery_increase = 2

    new_mastery = min(100, current_mastery + mastery_increase)

    db.execute("""
        INSERT INTO learning_progress (user_id, knowledge_point_id, mastery_percentage, socratic_rounds, last_socratic_at)
        VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
        mastery_percentage = ?,
        socratic_rounds = ?,
        last_socratic_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    """, (knowledge_id, new_mastery, new_rounds, new_mastery, new_rounds))

    if analysis.get("is_understanding_correct"):
        response = f"""太棒了！🎉 你的理解非常到位！

{analysis.get('feedback', '')}

📊 当前掌握度：{new_mastery}%"""
        if new_mastery >= 90:
            response += "\n\n🎉 恭喜！已达成90%掌握度！完成了苏格拉底问答验证，可以进入下一环节了！"
            hint = "🎉 达成90%掌握度！"
        elif new_rounds >= 3:
            response += f"\n\n📝 完成{new_rounds}轮问答，继续努力达到90%掌握度"
            hint = f"继续深入，当前掌握度{new_mastery}%"
        else:
            hint = f"苏格拉底问答进行中（{new_rounds}/轮）"
    elif analysis.get("needs_clarification"):
        response = f"""嗯，你的理解有偏差。让我帮你纠正一下：

{analysis.get('feedback', '')}

📊 当前掌握度：{new_mastery}%

{analysis.get('follow_up_question', '请进一步思考后重新回答')}"""
        hint = analysis.get('follow_up_question', '请进一步思考后重新回答')
    else:
        response = f"""好的，我收到了你的回答。

{analysis.get('feedback', '')}

📊 当前掌握度：{new_mastery}%

{analysis.get('follow_up_question', '继续深入思考')}"""
        hint = analysis.get('follow_up_question', '继续深入思考')

    return {
        "data": {
            "response": response,
            "socratic_hint": hint,
            "mastery_percentage": new_mastery,
            "socratic_rounds": new_rounds,
            "can_practice": new_mastery >= 90,
            "answer_quality": answer_quality,
            "knowledge_name": knowledge_name,
            "knowledge_id": knowledge_id,
            "mode": "socratic"
        }
    }


def determine_next_step(analysis: dict) -> str:
    """根据分析结果决定下一步"""
    if analysis.get("question_asked"):
        return ""

    questions = [
        "你能举个例子说明吗？",
        "这个概念和之前学的有什么联系？",
        "为什么会是这样呢？",
        "你能用自己的话重新描述一下吗？"
    ]

    return questions[analysis.get("depth_level", 0) % len(questions)]


@router.get("/history")
async def get_chat_history(knowledge_code: Optional[str] = None):
    """获取聊天历史"""
    if knowledge_code:
        result = db.fetch_all(
            """SELECT id, session_id, messages, status, created_at
               FROM user_sessions
               WHERE knowledge_point_id = (SELECT id FROM knowledge_points WHERE code = ?)
               ORDER BY created_at DESC LIMIT 50""",
            (knowledge_code,)
        )
    else:
        result = []

    return {"data": [
        {"session_id": r[1], "messages": r[2], "status": r[3], "time": r[4]}
        for r in result
    ]}