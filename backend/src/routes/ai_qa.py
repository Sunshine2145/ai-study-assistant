# AI Study Assistant - AI Q&A Module Routes

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from src.database.db import db
from src.modules.ai.feynman import FeynmanService
from src.config.settings import settings

router = APIRouter(prefix="/api/ai-qa", tags=["AI问答"])


class QARequest(BaseModel):
    question: str
    current_knowledge_id: Optional[int] = None


QA_PROMPT_TEMPLATE = """你是大王的学习助手，擅长用通俗易懂的语言解答学习疑问。

当前学习内容：{current_knowledge}

用户提问：{question}

解答要求：
1. 先确认用户的疑问点
2. 用生活化类比解释（避免术语堆砌）
3. 层层递进，从已知到未知
4. 识别并加粗标注关键知识点（用**包裹）
5. 引导用户思考："你理解了吗？"
6. 鼓励追问

格式要求：
- 关键知识点用**加粗**标注，方便用户点击查看详情
- 回答结构：确认问题 → 类比解释 → 回到知识点 → 引导思考
"""


@router.post("/chat")
async def qa_chat(request: QARequest):
    """AI问答 - 发送问题并获取回答"""
    current_knowledge = None

    if request.current_knowledge_id:
        kp = db.fetch_one(
            "SELECT name FROM knowledge_points WHERE id = ?",
            (request.current_knowledge_id,)
        )
        if kp:
            current_knowledge = kp[0]

    prompt = QA_PROMPT_TEMPLATE.format(
        current_knowledge=current_knowledge or "通用学习问题",
        question=request.question
    )

    feynman = FeynmanService(settings.ai.api_key, settings.ai.model)

    try:
        explanation = await feynman.explain(request.question, prompt)

        if explanation and not explanation.startswith("抱歉"):
            response = f"""🎯 **AI问答**

{explanation}

---

💡 继续提问，或返回学习页面继续学习"""
        else:
            response = f"""🎯 **AI问答**

抱歉，暂时无法回答这个问题。请稍后重试。

💡 你也可以在学习页面中直接提问。"""

        return {
            "data": {
                "response": response,
                "question": request.question
            }
        }
    except Exception as e:
        logger.error(f"AI Q&A error: {e}")
        return {
            "data": {
                "response": "AI服务暂时不可用，请稍后重试。",
                "question": request.question
            }
        }


@router.get("/knowledge-card/{term}")
async def get_knowledge_card(term: str):
    """获取知识点卡片详情"""
    # 先从knowledge_points表查询
    kp = db.fetch_one(
        """SELECT id, code, name, chapter FROM knowledge_points
           WHERE name LIKE ? OR code LIKE ? LIMIT 1""",
        (f"%{term}%", f"%{term}%")
    )

    if kp:
        knowledge_id, code, name, chapter = kp

        # 查询详细内容
        detail = db.fetch_one(
            "SELECT content, key_concepts FROM knowledge_detail WHERE knowledge_point_id = ?",
            (knowledge_id,)
        )

        content = detail[0] if detail else f"这是关于{name}的知识点"
        key_concepts = detail[1] if detail else ""

        # 查询相关题目
        questions = db.fetch_all(
            "SELECT content FROM questions WHERE knowledge_point_id = ? LIMIT 3",
            (knowledge_id,)
        )
        related_questions = [q[0] for q in questions] if questions else []

        # 查询关联知识点
        related_kps = db.fetch_all(
            """SELECT name, status FROM knowledge_points
               WHERE chapter = ? AND id != ? LIMIT 5""",
            (chapter, knowledge_id)
        )
        related_knowledge = [
            {"name": r[0], "status": r[1]}
            for r in related_kps
        ] if related_kps else []

        return {
            "data": {
                "success": True,
                "term": name,
                "definition": content[:200] + "..." if len(content) > 200 else content,
                "example": f"在系统架构中，{name}是一个重要的概念。",
                "related_knowledge": related_knowledge,
                "related_questions": related_questions,
                "code": code,
                "chapter": chapter
            }
        }

    # 如果没有找到，返回通用卡片
    return {
        "data": {
            "success": True,
            "term": term,
            "definition": f"{term}是系统架构中的一个重要概念。",
            "example": f"在实际项目中，{term}常用于解决特定问题。",
            "related_knowledge": [],
            "related_questions": [],
            "code": "",
            "chapter": ""
        }
    }


@router.get("/history")
async def get_qa_history():
    """获取AI问答历史"""
    # 暂时返回空历史，后续可扩展
    return {"data": []}
