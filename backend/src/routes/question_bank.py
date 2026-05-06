# AI Study Assistant - Question Bank Routes

from fastapi import APIRouter, Query
from typing import Optional
import json

from src.database.db import db

router = APIRouter(prefix="/api/question-bank", tags=["题库"])


@router.get("/list")
async def get_question_banks():
    """获取题库列表（按来源分组）"""
    results = db.fetch_all(
        """SELECT source, COUNT(*) as count,
           SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count
           FROM questions
           GROUP BY source
           ORDER BY COUNT(*) DESC"""
    )

    banks = []
    for r in results:
        source = r[0] or '未分类'
        total = r[1] or 0
        approved = r[2] or 0
        banks.append({
            "source": source,
            "total": total,
            "approved": approved,
            "pending": total - approved
        })

    return {"data": banks}


@router.get("/questions")
async def get_questions(
    source: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取题目列表"""
    conditions = []
    params = []

    if source:
        conditions.append("source = ?")
        params.append(source)
    if knowledge_point:
        conditions.append("knowledge_point = ?")
        params.append(knowledge_point)
    if type:
        conditions.append("type = ?")
        params.append(type)
    if status:
        conditions.append("status = ?")
        params.append(status)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Get total count
    count_result = db.fetch_one(
        f"SELECT COUNT(*) FROM questions WHERE {where_clause}",
        tuple(params)
    )
    total = count_result[0] if count_result else 0

    # Get paginated results
    offset = (page - 1) * page_size
    results = db.fetch_all(
        f"""SELECT id, type, content, options, answer, analysis, knowledge_point, source, status, created_at
           FROM questions
           WHERE {where_clause}
           ORDER BY id DESC
           LIMIT ? OFFSET ?""",
        tuple(params) + (page_size, offset)
    )

    questions = []
    for r in results:
        content = r[2] or ''
        # Handle content encoding
        if content:
            try:
                content = content.encode('utf-8').decode('utf-8')
            except:
                content = str(content)

        options = r[3] or '{}'
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except:
                options = {}

        questions.append({
            "id": r[0],
            "type": r[1],
            "content": content,
            "options": options,
            "answer": r[4],
            "analysis": r[5],
            "knowledge_point": r[6],
            "source": r[7],
            "status": r[8],
            "created_at": r[9]
        })

    return {
        "data": questions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    }


@router.get("/stats")
async def get_question_stats():
    """获取题库统计信息"""
    total = db.fetch_one("SELECT COUNT(*) FROM questions")[0] or 0
    approved = db.fetch_one("SELECT COUNT(*) FROM questions WHERE status = 'approved'")[0] or 0
    pending = db.fetch_one("SELECT COUNT(*) FROM questions WHERE status = 'pending'")[0] or 0

    by_type = db.fetch_all(
        """SELECT type, COUNT(*) as count
           FROM questions GROUP BY type"""
    )

    by_source = db.fetch_all(
        """SELECT source, COUNT(*) as count
           FROM questions GROUP BY source
           ORDER BY count DESC LIMIT 10"""
    )

    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "by_type": [{"type": r[0], "count": r[1]} for r in by_type],
        "by_source": [{"source": r[0] or "未分类", "count": r[1]} for r in by_source]
    }


@router.delete("/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    return {"message": "删除成功"}


@router.put("/{question_id}/status")
async def update_question_status(question_id: int, status: str):
    """更新题目状态"""
    db.execute(
        "UPDATE questions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, question_id)
    )
    return {"message": "状态更新成功"}


@router.post("/approve/{question_id}")
async def approve_question(question_id: int):
    """批准题目"""
    db.execute(
        "UPDATE questions SET status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (question_id,)
    )
    return {"message": "题目已批准"}