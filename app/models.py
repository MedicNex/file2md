from pydantic import BaseModel
from typing import Optional

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