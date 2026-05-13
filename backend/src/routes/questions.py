# AI Study Assistant - Questions Routes

import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from src.modules.question import question_service

router = APIRouter(prefix="/api/questions", tags=["题目"])


class QuestionCreate(BaseModel):
    type: str = "single"
    content: str
    options: Optional[dict] = {}
    answer: str
    analysis: Optional[str] = ""
    knowledge_point: Optional[str] = ""
    difficulty: Optional[int] = 1
    source: Optional[str] = "manual"
    status: Optional[str] = "pending"


class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    options: Optional[dict] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    knowledge_point: Optional[str] = None
    difficulty: Optional[int] = None
    source: Optional[str] = None
    status: Optional[str] = None


class QuestionImportRequest(BaseModel):
    questions: List[dict]
    knowledge_point: Optional[str] = None
    source: Optional[str] = "manual"


@router.get("")
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    source: Optional[str] = None,
):
    """获取题目列表（分页+过滤）"""
    filters = {}
    if type:
        filters["type"] = type
    if status:
        filters["status"] = status
    if knowledge_point:
        filters["knowledge_point"] = knowledge_point
    if source:
        filters["source"] = source
    return question_service.list_all(filters, page, page_size)


@router.get("/export")
async def export_questions(
    type: Optional[str] = None,
    status: Optional[str] = None,
    knowledge_point: Optional[str] = None,
):
    """导出题目"""
    filters = {}
    if type:
        filters["type"] = type
    if status:
        filters["status"] = status
    if knowledge_point:
        filters["knowledge_point"] = knowledge_point
    result = question_service.list_all(filters, page=1, page_size=10000)
    return {"data": result["data"]}


@router.get("/{knowledge_id}")
async def get_questions(knowledge_id: int):
    """获取知识点的题目"""
    result = question_service.list_all(
        filters={"knowledge_point": str(knowledge_id), "status": "approved"},
        page=1, page_size=5
    )
    if result["data"]:
        return {"data": result["data"]}

    sample = _get_sample_questions(knowledge_id)
    return {"data": sample}


@router.post("")
async def create_question(data: QuestionCreate):
    """创建题目"""
    q_id = question_service.create(data.dict())
    return {"id": q_id, "message": "创建成功"}


@router.put("/{question_id}")
async def update_question(question_id: int, data: QuestionUpdate):
    """更新题目"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的字段")
    if not question_service.update(question_id, update_data):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "更新成功"}


@router.delete("/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    if not question_service.delete(question_id):
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "删除成功"}


@router.post("/import")
async def import_questions(data: QuestionImportRequest):
    """批量导入题目"""
    imported = question_service.batch_import(data.questions, data.knowledge_point, data.source)
    return {"imported": imported, "message": f"成功导入 {imported} 道题目"}


def _get_sample_questions(knowledge_id: int) -> list:
    """获取示例题目"""
    if knowledge_id == 1:
        return [
            {"id": 1001, "type": "single", "content": "下列关于Cache的说法，错误的是？",
             "options": {"A": "位于CPU和内存之间", "B": "容量比内存大", "C": "访问速度比内存快", "D": "由高速SRAM组成"},
             "answer": "B", "analysis": "Cache的容量通常比内存小很多。"},
            {"id": 1002, "type": "single", "content": "在Cache系统中，采用的替换算法不包括？",
             "options": {"A": "FIFO", "B": "LRU", "C": "OPT", "D": "LFU"},
             "answer": "C", "analysis": "OPT是理想状态下的算法，无法实际实现。"},
            {"id": 1003, "type": "judge", "content": "Cache的命中率越高越好，没有负面影响。",
             "options": {"A": "对", "B": "错"}, "answer": "false",
             "analysis": "提高Cache命中率会增加复杂度。"},
            {"id": 1004, "type": "single", "content": "多级Cache比单级Cache更能提高命中率。",
             "options": {"A": "正确，级数越多越好", "B": "错误，多级Cache会降低命中率",
                         "C": "正确，但级数过多会增加延迟", "D": "错误，多级Cache没有意义"},
             "answer": "C", "analysis": "多级Cache确实能提高命中率，但级数过多会增加延迟。"},
            {"id": 1005, "type": "multi", "content": "下列属于Cache写策略的有？",
             "options": {"A": "写直达", "B": "写回法", "C": "预取", "D": "替换"},
             "answer": ["A", "B"], "analysis": "Cache写策略包括写直达和写回法。"}
        ]
    return [
        {"id": knowledge_id * 100, "type": "single",
         "content": f"关于知识点{knowledge_id}的练习题，答案选择最合适的选项。",
         "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
         "answer": "B", "analysis": "这是示例题目的解析。"}
    ]
