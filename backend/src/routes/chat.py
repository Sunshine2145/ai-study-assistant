# AI Study Assistant - Chat Routes

import json
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


TRANSITION_KEYWORDS = ["学习好了", "可以了", "开始检验", "准备好了", "掌握了", "我学会了"]


@router.post("")
async def send_message(request: ChatRequest):
    """处理用户聊天消息 — 三阶段路由"""
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
                "knowledge_name": None,
                "learning_phase": "feynman"
            }
        }

    # 查询当前学习阶段
    progress = db.fetch_one(
        "SELECT learning_phase FROM learning_progress WHERE knowledge_point_id = ?",
        (knowledge_id,)
    )
    phase = progress[0] if progress else "feynman"

    # Phase 1: 费曼学习 → 自动返回讲解，然后进入互动阶段
    if phase == "feynman":
        result = await _generate_feynman_explanation(knowledge_id, knowledge_code, knowledge_name)
        _update_phase(knowledge_id, "interactive")
        result["data"]["learning_phase"] = "interactive"
        return result

    # Phase 2: 互动学习
    if phase == "interactive":
        user_lower = request.content.lower()
        if any(kw in user_lower for kw in TRANSITION_KEYWORDS):
            return await _start_socratic_phase(knowledge_id, knowledge_code, knowledge_name)
        else:
            return await _handle_interactive_chat(knowledge_id, knowledge_code, knowledge_name, request.content)

    # Phase 3: 苏格拉底检验
    if phase == "socratic":
        return await _process_socratic_answer(knowledge_id, knowledge_code, knowledge_name, request.content)

    # 默认：返回费曼讲解
    result = await _generate_feynman_explanation(knowledge_id, knowledge_code, knowledge_name)
    _update_phase(knowledge_id, "interactive")
    result["data"]["learning_phase"] = "interactive"
    return result


def _update_phase(knowledge_id: int, phase: str):
    """更新学习阶段"""
    db.execute("""
        INSERT INTO learning_progress (user_id, knowledge_point_id, learning_phase, mastery_percentage, socratic_rounds)
        VALUES (1, ?, ?, 0, 0)
        ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
        learning_phase = ?,
        updated_at = CURRENT_TIMESTAMP
    """, (knowledge_id, phase, phase))


def _get_socratic_history(knowledge_id: int) -> list:
    """获取苏格拉底问答历史"""
    progress = db.fetch_one(
        "SELECT socratic_history FROM learning_progress WHERE knowledge_point_id = ?",
        (knowledge_id,)
    )
    if progress and progress[0]:
        try:
            return json.loads(progress[0])
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def _save_socratic_history(knowledge_id: int, history: list):
    """保存苏格拉底问答历史"""
    db.execute("""
        UPDATE learning_progress
        SET socratic_history = ?
        WHERE knowledge_point_id = ?
    """, (json.dumps(history, ensure_ascii=False), knowledge_id))


async def _generate_feynman_explanation(knowledge_id: int, knowledge_code: str, knowledge_name: str):
    """Phase 1: 生成费曼讲解"""
    feynman = FeynmanService(settings.ai.api_key, settings.ai.model)

    try:
        explanation = await feynman.explain(knowledge_name, "")

        if explanation and not explanation.startswith("抱歉"):
            response = f"""📚 **费曼学习法讲解：{knowledge_name}**

{explanation}

---

💡 **互动学习阶段**：现在你可以：
• 输入你对这个知识点的疑问，我会为你解答
• 输入「学习好了」进入苏格拉底检验环节"""
        else:
            response = f"""📚 **关于 {knowledge_name}**

AI服务暂时不可用。请用自己的话简要描述一下这个概念，然后输入「学习好了」进入检验环节。"""

        return {
            "data": {
                "response": response,
                "socratic_hint": f"费曼学习 → {knowledge_name}",
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

请试着用自己的话描述一下这个知识点，然后输入「学习好了」进入检验环节。""",
                "socratic_hint": f"费曼学习 → {knowledge_name}",
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "feynman"
            }
        }


async def _handle_interactive_chat(knowledge_id: int, knowledge_code: str, knowledge_name: str, user_message: str):
    """Phase 2: 互动学习 — AI回答用户关于知识点的提问"""
    feynman = FeynmanService(settings.ai.api_key, settings.ai.model)

    try:
        explanation = await feynman.explain(knowledge_name, user_message)

        if explanation and not explanation.startswith("抱歉"):
            response = f"""💬 **互动学习**

{explanation}

---

💡 继续提问，或输入「学习好了」进入苏格拉底检验环节"""
        else:
            response = f"""💬 **互动学习**

AI服务暂时不可用，请稍后重试。

💡 你也可以输入「学习好了」直接进入检验环节。"""

        return {
            "data": {
                "response": response,
                "socratic_hint": f"互动学习 → {knowledge_name}",
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "interactive",
                "learning_phase": "interactive"
            }
        }
    except Exception as e:
        logger.error(f"Interactive chat error: {e}")
        return {
            "data": {
                "response": "AI服务暂时不可用，请稍后重试。",
                "socratic_hint": f"互动学习 → {knowledge_name}",
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "interactive",
                "learning_phase": "interactive"
            }
        }


async def _start_socratic_phase(knowledge_id: int, knowledge_code: str, knowledge_name: str):
    """Phase 3: 初始化苏格拉底检验 — 使用AI生成第一个问题"""
    _update_phase(knowledge_id, "socratic")

    # 重置掌握度、轮次和历史
    db.execute("""
        UPDATE learning_progress
        SET mastery_percentage = 0, socratic_rounds = 0, socratic_history = '[]'
        WHERE knowledge_point_id = ?
    """, (knowledge_id,))

    # 使用AI生成第一个引导问题
    socratic = SocraticService(api_key=settings.ai.api_key)
    result = await socratic.generate_question(knowledge_name, knowledge_code, level=0, history=[])
    first_question = result["question"]

    response = f"""🎯 **苏格拉底检验开始！**

针对 **{knowledge_name}** 进行检验，通过回答问题达到90%掌握度即可解锁下一个知识点。

**问题**：{first_question}"""

    return {
        "data": {
            "response": response,
            "socratic_hint": f"苏格拉底检验 → {knowledge_name}",
            "mastery_percentage": 0,
            "socratic_rounds": 0,
            "knowledge_name": knowledge_name,
            "knowledge_id": knowledge_id,
            "mode": "socratic",
            "learning_phase": "socratic"
        }
    }


async def _process_socratic_answer(knowledge_id: int, knowledge_code: str, knowledge_name: str, user_message: str):
    """Phase 3: 处理苏格拉底检验的回答 — 使用AI分析"""
    progress = db.fetch_one("""
        SELECT mastery_percentage, socratic_rounds
        FROM learning_progress
        WHERE knowledge_point_id = ?
    """, (knowledge_id,))

    current_mastery = progress[0] if progress else 0
    current_rounds = progress[1] if progress else 0

    # 获取问答历史
    history = _get_socratic_history(knowledge_id)

    # 获取上一个问题
    last_question = history[-2] if len(history) >= 2 else f"关于{knowledge_name}的理解"

    # 使用AI分析回答
    socratic = SocraticService(api_key=settings.ai.api_key)
    analysis = await socratic.analyze_answer(knowledge_name, last_question, user_message, history)

    mastery_delta = analysis.get("mastery_delta", 5)
    new_rounds = current_rounds + 1
    new_mastery = min(100, current_mastery + mastery_delta)

    # 更新历史（添加问题和回答）
    history.append(last_question)
    history.append(user_message)

    # 达到90%掌握度 → 完成
    if new_mastery >= 90:
        db.execute("""
            UPDATE learning_progress
            SET mastery_percentage = ?, socratic_rounds = ?, learning_phase = 'completed',
                feynman_completed = 1, feynman_completed_at = CURRENT_TIMESTAMP,
                last_socratic_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP,
                socratic_history = ?
            WHERE knowledge_point_id = ?
        """, (new_mastery, new_rounds, json.dumps(history, ensure_ascii=False), knowledge_id))

        _complete_and_unlock(knowledge_id)

        response = f"""🎉 **恭喜！已掌握 {knowledge_name}！**

{analysis.get('feedback', '')}

📊 最终掌握度：{new_mastery}% | 共{new_rounds}轮问答

✅ 已解锁下一个知识点，前往学习地图查看！"""

        return {
            "data": {
                "response": response,
                "socratic_hint": "学习完成！前往地图选择下一个知识点",
                "mastery_percentage": new_mastery,
                "socratic_rounds": new_rounds,
                "can_practice": True,
                "answer_quality": analysis.get("answer_quality", 50),
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "socratic",
                "learning_phase": "completed"
            }
        }

    # 超过5轮且未达标 → 本轮结束
    if new_rounds >= SocraticService.MAX_QUESTIONS:
        db.execute("""
            UPDATE learning_progress
            SET mastery_percentage = ?, socratic_rounds = ?, learning_phase = 'feynman',
                last_socratic_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP,
                socratic_history = '[]'
            WHERE knowledge_point_id = ?
        """, (new_mastery, new_rounds, knowledge_id))

        response = f"""📋 **本轮检验结束**

{analysis.get('feedback', '')}

📊 当前掌握度：{new_mastery}%（需要达到90%）

你还需要重新学习这个知识点。输入任意内容重新开始费曼学习。"""

        return {
            "data": {
                "response": response,
                "socratic_hint": f"掌握度 {new_mastery}% — 需要重新学习",
                "mastery_percentage": new_mastery,
                "socratic_rounds": new_rounds,
                "can_practice": False,
                "answer_quality": analysis.get("answer_quality", 50),
                "knowledge_name": knowledge_name,
                "knowledge_id": knowledge_id,
                "mode": "socratic",
                "learning_phase": "feynman"
            }
        }

    # 未达标，继续检验
    db.execute("""
        INSERT INTO learning_progress (user_id, knowledge_point_id, mastery_percentage, socratic_rounds, learning_phase, last_socratic_at, socratic_history)
        VALUES (1, ?, ?, ?, 'socratic', CURRENT_TIMESTAMP, ?)
        ON CONFLICT(user_id, knowledge_point_id) DO UPDATE SET
        mastery_percentage = ?,
        socratic_rounds = ?,
        last_socratic_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP,
        socratic_history = ?
    """, (knowledge_id, new_mastery, new_rounds, json.dumps(history, ensure_ascii=False),
          new_mastery, new_rounds, json.dumps(history, ensure_ascii=False)))

    # 生成下一个问题
    next_level = min(new_rounds, len(SocraticService.LEVELS) - 1)
    next_q_result = await socratic.generate_question(knowledge_name, knowledge_code, next_level, history)
    next_question = next_q_result["question"]

    feedback = analysis.get("feedback", "")
    follow_up = next_question

    if analysis.get("is_understanding_correct"):
        response = f"""太棒了！🎉 你的理解非常到位！

{feedback}

📊 当前掌握度：{new_mastery}%（需要达到90%）

{follow_up}"""
        hint = f"掌握度 {new_mastery}% — 继续深入"
    elif analysis.get("needs_clarification"):
        response = f"""嗯，你的理解有偏差。让我帮你纠正一下：

{feedback}

📊 当前掌握度：{new_mastery}%

{follow_up}"""
        hint = f"掌握度 {new_mastery}% — 纠正理解中"
    else:
        response = f"""好的，我收到了你的回答。

{feedback}

📊 当前掌握度：{new_mastery}%

{follow_up}"""
        hint = f"掌握度 {new_mastery}% — 继续深入"

    return {
        "data": {
            "response": response,
            "socratic_hint": hint,
            "mastery_percentage": new_mastery,
            "socratic_rounds": new_rounds,
            "can_practice": new_mastery >= 90,
            "answer_quality": analysis.get("answer_quality", 50),
            "knowledge_name": knowledge_name,
            "knowledge_id": knowledge_id,
            "mode": "socratic",
            "learning_phase": "socratic"
        }
    }


def _complete_and_unlock(knowledge_id: int):
    """标记知识点完成并解锁下一个"""
    current_kp = db.fetch_one(
        "SELECT code, sort_order FROM knowledge_points WHERE id = ?",
        (knowledge_id,)
    )
    if not current_kp:
        return

    db.execute(
        "UPDATE knowledge_points SET status = 'completed' WHERE id = ?",
        (knowledge_id,)
    )

    next_kp = db.fetch_one("""
        SELECT id, code, name FROM knowledge_points
        WHERE sort_order > ? AND status = 'locked'
        ORDER BY sort_order LIMIT 1
    """, (current_kp[1],))

    if next_kp:
        db.execute(
            "UPDATE knowledge_points SET status = 'unlocked' WHERE id = ?",
            (next_kp[0],)
        )
        logger.info(f"Unlocked next knowledge point: {next_kp[1]} - {next_kp[2]}")


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
