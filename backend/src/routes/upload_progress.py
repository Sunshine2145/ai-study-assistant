# AI Study Assistant - Upload Progress Routes

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from src.database.db import db

router = APIRouter(prefix="/api/upload", tags=["上传"])


class UploadProgressResponse(BaseModel):
    id: int
    file_name: str
    file_size: int
    status: str
    progress: int
    stage: str
    total_questions: int
    processed_questions: int
    error_message: Optional[str] = None


@router.post("/progress")
async def create_upload_progress(file_name: str, file_size: int):
    """创建上传任务"""
    # Use user_id = 1 for now (default user)
    user_id = 1

    cursor = db.execute(
        """INSERT INTO upload_progress (user_id, file_name, file_size, status, progress, stage)
           VALUES (%s, %s, %s, 'processing', 0, 'file_uploaded')""",
        (user_id, file_name, file_size)
    )

    upload_id = cursor.lastrowid

    return {
        "id": upload_id,
        "file_name": file_name,
        "message": "上传任务创建成功"
    }


@router.get("/progress/{upload_id}")
async def get_upload_progress(upload_id: int):
    """获取上传进度"""
    result = db.fetch_one(
        """SELECT id, file_name, file_size, status, progress, stage,
                  total_questions, processed_questions, error_message
           FROM upload_progress WHERE id = %s""",
        (upload_id,)
    )

    if not result:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    return {
        "id": result['id'],
        "file_name": result['file_name'],
        "file_size": result['file_size'],
        "status": result['status'],
        "progress": result['progress'],
        "stage": result['stage'],
        "total_questions": result['total_questions'],
        "processed_questions": result['processed_questions'],
        "error_message": result['error_message']
    }


@router.put("/progress/{upload_id}")
async def update_upload_progress(
    upload_id: int,
    progress: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    total_questions: Optional[int] = None,
    processed_questions: Optional[int] = None,
    error_message: Optional[str] = None
):
    """更新上传进度"""
    existing = db.fetch_one("SELECT id FROM upload_progress WHERE id = %s", (upload_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    updates = []
    params = []

    if progress is not None:
        updates.append("progress = %s")
        params.append(progress)
    if stage:
        updates.append("stage = %s")
        params.append(stage)
    if status:
        updates.append("status = %s")
        params.append(status)
    if total_questions is not None:
        updates.append("total_questions = %s")
        params.append(total_questions)
    if processed_questions is not None:
        updates.append("processed_questions = %s")
        params.append(processed_questions)
    if error_message:
        updates.append("error_message = %s")
        params.append(error_message)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(upload_id)
        db.execute(f"UPDATE upload_progress SET {', '.join(updates)} WHERE id = %s", tuple(params))

    return {"message": "进度更新成功"}


@router.get("/progress/{upload_id}/status")
async def get_upload_status(upload_id: int):
    """获取简化的上传状态"""
    result = db.fetch_one(
        "SELECT status, progress, stage FROM upload_progress WHERE id = %s",
        (upload_id,)
    )

    if not result:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    return {
        "status": result['status'],
        "progress": result['progress'],
        "stage": result['stage']
    }
