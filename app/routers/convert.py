from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import os
import time
import tempfile
from pathlib import Path

from app.auth import get_api_key
from app.models import ConvertResponse, ErrorResponse
from app.parsers.registry import parser_registry

router = APIRouter()

@router.post("/convert", response_model=ConvertResponse)
async def convert_file(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    将上传的文件转换为Markdown格式
    """
    start_time = time.time()
    temp_file_path = None
    parser_instance = None
    
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_FILE",
                    "message": "文件名不能为空"
                }
            )
        
        # 获取文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        
        # 检查是否支持该文件类型
        if not parser_registry.is_supported(file_extension):
            supported_exts = parser_registry.get_supported_extensions()
            raise HTTPException(
                status_code=415,
                detail={
                    "code": "UNSUPPORTED_TYPE",
                    "message": f"不支持的文件类型: {file_extension}",
                    "supported_types": supported_exts
                }
            )
        
        # 保存上传的文件到临时位置
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name
        
        # 写入文件内容
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # 获取解析器
        parser_class = parser_registry.get_parser(file_extension)
        parser_instance = parser_class()
        
        # 解析文件
        markdown_content = await parser_instance.parse(temp_file_path)
        
        # 计算处理时间
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"文件转换成功: {file.filename} ({len(content)} bytes) -> {len(markdown_content)} characters")
        
        return ConvertResponse(
            filename=file.filename,
            size=len(content),
            content_type=file.content_type or "application/octet-stream",
            content=markdown_content,
            duration_ms=duration_ms
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        logger.error(f"文件转换失败 {file.filename}: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "code": "PARSE_ERROR",
                "message": "文件解析失败",
                "detail": str(e)
            }
        )
        
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"临时文件清理失败: {cleanup_error}")
        
        # 清理解析器临时文件
        if parser_instance:
            try:
                parser_instance.cleanup()
            except Exception as cleanup_error:
                logger.warning(f"解析器清理失败: {cleanup_error}")

@router.get("/supported-types")
async def get_supported_types(api_key: str = Depends(get_api_key)):
    """
    获取支持的文件类型列表
    """
    return {
        "supported_extensions": parser_registry.get_supported_extensions(),
        "total_count": len(parser_registry.get_supported_extensions())
    } 