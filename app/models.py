from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ConvertResponse(BaseModel):
    """转换响应模型"""
    filename: str
    size: int
    content_type: str
    content: str
    duration_ms: int

class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: str
    message: str
    detail: Optional[str] = None

class TaskSubmitResponse(BaseModel):
    """任务提交响应模型"""
    task_id: str
    message: str
    filename: str
    status: str

class BatchSubmitResponse(BaseModel):
    """批量提交响应模型"""
    submitted_tasks: List[TaskSubmitResponse]
    total_count: int
    success_count: int
    failed_count: int

class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None

class QueueInfoResponse(BaseModel):
    """队列信息响应模型"""
    max_concurrent: int
    queue_size: int
    active_tasks: int
    total_tasks: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int 