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
           VALUES (?, ?, ?, 'processing', 0, 'file_uploaded')""",
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
           FROM upload_progress WHERE id = ?""",
        (upload_id,)
    )

    if not result:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    return {
        "id": result[0],
        "file_name": result[1],
        "file_size": result[2],
        "status": result[3],
        "progress": result[4],
        "stage": result[5],
        "total_questions": result[6],
        "processed_questions": result[7],
        "error_message": result[8]
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
    existing = db.fetch_one("SELECT id FROM upload_progress WHERE id = ?", (upload_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    updates = []
    params = []

    if progress is not None:
        updates.append("progress = ?")
        params.append(progress)
    if stage:
        updates.append("stage = ?")
        params.append(stage)
    if status:
        updates.append("status = ?")
        params.append(status)
    if total_questions is not None:
        updates.append("total_questions = ?")
        params.append(total_questions)
    if processed_questions is not None:
        updates.append("processed_questions = ?")
        params.append(processed_questions)
    if error_message:
        updates.append("error_message = ?")
        params.append(error_message)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(upload_id)
        db.execute(f"UPDATE upload_progress SET {', '.join(updates)} WHERE id = ?", tuple(params))

    return {"message": "进度更新成功"}


@router.get("/progress/{upload_id}/status")
async def get_upload_status(upload_id: int):
    """获取简化的���传状态"""
    result = db.fetch_one(
        "SELECT status, progress, stage FROM upload_progress WHERE id = ?",
        (upload_id,)
    )

    if not result:
        raise HTTPException(status_code=404, detail="上传任务不存在")

    return {
        "status": result[0],
        "progress": result[1],
        "stage": result[2]
    }