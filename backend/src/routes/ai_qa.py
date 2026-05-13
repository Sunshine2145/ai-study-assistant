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


def _get_local_answer(question: str, current_knowledge: Optional[str] = None) -> str:
    """Generate a local answer using database knowledge when AI is unavailable"""
    # Try to find relevant knowledge points
    search_terms = question.strip()
    kps = db.fetch_all(
        """SELECT name, chapter FROM knowledge_points
           WHERE name LIKE %s LIMIT 5""",
        (f"%{search_terms[:20]}%",)
    )

    if kps:
        kp_lines = "\n".join([f"• **{k['name']}**（{k['chapter']}）" for k in kps])
        return f"""根据知识库查询，关于这个问题，找到以下相关知识点：

{kp_lines}

📚 **学习建议**：
1. 进入学习地图，选择对应章节开始系统学习
2. 使用费曼学习法，用自己的话复述概念
3. 通过苏格拉底提问检验掌握程度

💡 继续提问，或前往学习页面深入学习。"""

    if current_knowledge:
        return f"""关于 **{current_knowledge}**，这是一个重要的学习内容。

📚 **学习建议**：
1. 尝试用自己的话描述一下这个概念
2. 想想它在实际系统架构中有什么应用
3. 能否举出一个生活中的例子来类比？

💡 建议进入学习地图，使用费曼学习法系统学习这个知识点。"""

    return f"""收到你的问题：「{question}」

📚 **学习建议**：
1. 进入**学习地图**，浏览完整的知识章节树
2. 选择一个知识点，使用**费曼学习法**深入学习
3. 通过**苏格拉底提问**检验学习效果

💡 AI服务暂未配置API密钥，当前使用本地知识库模式。配置 DeepSeek API Key 后可使用完整AI能力。"""


@router.post("/chat")
async def qa_chat(request: QARequest):
    """AI问答 - 发送问题并获取回答"""
    current_knowledge = None

    if request.current_knowledge_id:
        kp = db.fetch_one(
            "SELECT name FROM knowledge_points WHERE id = %s",
            (request.current_knowledge_id,)
        )
        if kp:
            current_knowledge = kp['name']

    # Try AI if API key is configured
    if settings.ai.api_key:
        prompt = QA_PROMPT_TEMPLATE.format(
            current_knowledge=current_knowledge or "通用学习问题",
            question=request.question
        )

        feynman = FeynmanService(settings.ai.api_key, settings.ai.model, settings.ai.base_url)

        try:
            explanation = await feynman.explain(request.question, prompt)

            if explanation and not explanation.startswith("抱歉"):
                response = f"""🎯 **AI问答**

{explanation}

---

💡 继续提问，或返回学习页面继续学习"""
                return {"data": {"response": response, "question": request.question}}
        except Exception as e:
            logger.error(f"AI Q&A error: {e}")

    # Fallback to local knowledge base
    local_answer = _get_local_answer(request.question, current_knowledge)
    response = f"""🎯 **AI问答**（本地知识库模式）

{local_answer}"""
    return {"data": {"response": response, "question": request.question}}


@router.get("/knowledge-card/{term}")
async def get_knowledge_card(term: str):
    """获取知识点卡片详情"""
    kp = db.fetch_one(
        """SELECT id, code, name, chapter FROM knowledge_points
           WHERE name LIKE %s OR code LIKE %s LIMIT 1""",
        (f"%{term}%", f"%{term}%")
    )

    if kp:
        knowledge_id = kp['id']
        code = kp['code']
        name = kp['name']
        chapter = kp['chapter']

        detail = db.fetch_one(
            "SELECT content, key_concepts FROM knowledge_detail WHERE knowledge_point_id = %s",
            (knowledge_id,)
        )

        content = detail['content'] if detail else f"这是关于{name}的知识点"
        key_concepts = detail['key_concepts'] if detail else ""

        questions = db.fetch_all(
            "SELECT content FROM questions WHERE knowledge_point = %s LIMIT 3",
            (str(knowledge_id),)
        )
        related_questions = [q['content'] for q in questions] if questions else []

        related_kps = db.fetch_all(
            """SELECT name, status FROM knowledge_points
               WHERE chapter = %s AND id != %s LIMIT 5""",
            (chapter, knowledge_id)
        )
        related_knowledge = [
            {"name": r['name'], "status": r['status']}
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
    return {"data": []}
