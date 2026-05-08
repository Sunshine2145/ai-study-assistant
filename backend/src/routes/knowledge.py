# AI Study Assistant - Knowledge Routes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from src.modules.knowledge import knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["知识点"])


class KnowledgePointCreate(BaseModel):
    code: str
    name: str
    chapter: Optional[str] = ""
    stage: Optional[str] = ""
    sort_order: Optional[int] = 0
    status: Optional[str] = "locked"


class KnowledgePointUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    chapter: Optional[str] = None
    stage: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class KnowledgePointImport(BaseModel):
    items: List[KnowledgePointCreate]


@router.get("")
async def get_knowledge_points(stage: Optional[str] = None):
    """获取知识点列表"""
    return {"data": knowledge_service.list_all(stage)}


@router.get("/export")
async def export_knowledge_points():
    """导出所有知识点"""
    return {"data": knowledge_service.export_all()}


@router.get("/{code}")
async def get_knowledge_point(code: str):
    """获取指定知识点"""
    kp = knowledge_service.get_by_code(code)
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return kp


@router.post("")
async def create_knowledge_point(data: KnowledgePointCreate):
    """创建知识点"""
    try:
        kp_id = knowledge_service.create(data.dict())
        return {"id": kp_id, "message": "创建成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{kp_id}")
async def update_knowledge_point(kp_id: int, data: KnowledgePointUpdate):
    """更新知识点"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="没有要更新的字段")
    if not knowledge_service.update(kp_id, update_data):
        raise HTTPException(status_code=404, detail="知识点不存在")
    return {"message": "更新成功"}


@router.delete("/{kp_id}")
async def delete_knowledge_point(kp_id: int):
    """删除知识点"""
    try:
        if not knowledge_service.delete(kp_id):
            raise HTTPException(status_code=404, detail="知识点不存在")
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
async def import_knowledge_points(data: KnowledgePointImport):
    """批量导入知识点"""
    items = [item.dict() for item in data.items]
    imported = knowledge_service.batch_import(items)
    return {"imported": imported, "message": f"成功导入 {imported} 个知识点"}
