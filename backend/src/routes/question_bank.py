# AI Study Assistant - Question Bank Routes

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.modules.question import question_service

router = APIRouter(prefix="/api/question-bank", tags=["题库"])


@router.get("/list")
async def get_question_banks():
    """获取题库列表（按来源分组）"""
    return {"data": question_service.get_banks()}


@router.delete("/bank")
async def delete_bank(source: str = Query(..., description="题库来源")):
    """删除整个题库（按来源）"""
    count = question_service.delete_by_source(source)
    if count == 0:
        raise HTTPException(status_code=404, detail="题库不存在或已为空")
    return {"message": f"已删除题库「{source}」，共移除 {count} 道题目"}


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
    filters = {}
    if source:
        filters["source"] = source
    if knowledge_point:
        filters["knowledge_point"] = knowledge_point
    if type:
        filters["type"] = type
    if status:
        filters["status"] = status
    return question_service.list_all(filters, page, page_size)


@router.get("/stats")
async def get_question_stats():
    """获取题库统计信息"""
    return question_service.get_stats()


@router.delete("/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    if not question_service.delete(question_id):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "删除成功"}


@router.put("/{question_id}/status")
async def update_question_status(question_id: int, status: str):
    """更新题目状态"""
    if not question_service.update_status(question_id, status):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "状态更新成功"}


@router.post("/approve/{question_id}")
async def approve_question(question_id: int):
    """批准题目"""
    if not question_service.update_status(question_id, "approved"):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "题目已批准"}
