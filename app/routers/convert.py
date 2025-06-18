from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import os
import time
import tempfile
from pathlib import Path
import json
from typing import List

from app.config import config
from app.auth import get_api_key
from app.models import (
    ConvertResponse, ErrorResponse, TaskSubmitResponse, 
    BatchSubmitResponse, TaskStatusResponse, QueueInfoResponse,
    CacheStatsResponse
)
from app.parsers.registry import parser_registry
from app.queue_manager import TaskStatus
from app.cache import cache_manager

# 自定义JSON响应类，确保中文字符正确显示
class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

def log_conversion_result(filename: str, content: str, file_size: int) -> None:
    """
    记录转换结果的摘要信息
    
    Args:
        filename: 文件名
        content: 转换后的内容
        file_size: 原文件大小
    """
    content_length = len(content)
    logger.info(f"文件转换成功: {filename} ({file_size} bytes) -> {content_length} characters")
    
    if config.ENABLE_DETAILED_LOGGING:
        if content_length <= config.MAX_LOG_CONTENT_LENGTH * 2:
            logger.debug(f"转换结果内容:\n{content}")
        else:
            # 记录开头和结尾的部分内容
            start_content = content[:config.MAX_LOG_CONTENT_LENGTH]
            end_content = content[-config.MAX_LOG_CONTENT_LENGTH:]
            logger.debug(f"转换结果内容（前{config.MAX_LOG_CONTENT_LENGTH}字符）:\n{start_content}")
            logger.debug(f"转换结果内容（后{config.MAX_LOG_CONTENT_LENGTH}字符）:\n...{end_content}")
    else:
        # 只记录摘要信息
        lines_count = content.count('\n') + 1
        logger.info(f"转换结果摘要: {content_length} 字符, {lines_count} 行")

router = APIRouter()

@router.post("/convert", response_model=ConvertResponse)
async def convert_file(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    将上传的文件转换为Markdown格式（单文件同步转换）
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
        
        # 先快速读取文件内容用于缓存检查
        content = await file.read()
        file_size = len(content)
        
        # 检查文件大小
        if file_size == 0:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "EMPTY_FILE",
                    "message": "文件为空"
                }
            )
        
        if file_size > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "code": "FILE_TOO_LARGE",
                    "message": f"文件过大: {file_size} bytes，最大允许: {config.MAX_FILE_SIZE} bytes ({config.MAX_FILE_SIZE // 1024 // 1024} MB)"
                }
            )
        
        # 优先检查缓存，避免不必要的文件处理
        cache_check_start = time.time()
        cached_result = await cache_manager.get_cached_result(content)
        if cached_result:
            # 计算缓存检查的实际耗时
            cache_duration_ms = int((time.time() - cache_check_start) * 1000)
            total_duration_ms = int((time.time() - start_time) * 1000)
            
            # 返回缓存的结果，但更新文件名和时间信息
            cached_result["filename"] = file.filename
            cached_result["cache_duration_ms"] = cache_duration_ms
            cached_result["total_duration_ms"] = total_duration_ms
            
            logger.info(f"从缓存返回结果: {file.filename} (缓存查询: {cache_duration_ms}ms, 总耗时: {total_duration_ms}ms)")
            return UnicodeJSONResponse(content=cached_result)
        
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
        temp_file.write(content)
        temp_file.close()
        
        # 获取解析器
        parser_class = parser_registry.get_parser(file_extension)
        parser_instance = parser_class()
        
        # 解析文件
        markdown_content = await parser_instance.parse(temp_file_path)
        
        # 计算处理时间
        duration_ms = int((time.time() - start_time) * 1000)
        
        log_conversion_result(file.filename, markdown_content, len(content))
        
        # 缓存解析结果
        await cache_manager.cache_result(
            file_content=content,
            filename=file.filename,
            markdown_content=markdown_content,
            file_size=file_size,
            duration_ms=duration_ms,
            content_type=file.content_type
        )
        
        # 使用自定义响应类确保中文正确显示
        response_data = {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type or "application/octet-stream",
            "content": markdown_content,
            "duration_ms": duration_ms,
            "from_cache": False
        }
        
        return UnicodeJSONResponse(content=response_data)
        
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

@router.post("/convert-batch", response_model=BatchSubmitResponse)
async def convert_batch_files(
    files: List[UploadFile] = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    批量提交文件转换任务到队列（异步处理，基于配置的并发数）
    """
    # 获取队列管理器实例
    from app.main import queue_manager
    
    # 确保队列管理器已启动
    await queue_manager.start_worker()
    
    submitted_tasks = []
    success_count = 0
    failed_count = 0
    
    for file in files:
        try:
            # 提交任务到队列
            task_id = await queue_manager.submit_task(file)
            
            submitted_tasks.append(TaskSubmitResponse(
                task_id=task_id,
                message="任务已提交到转换队列",
                filename=file.filename,
                status="pending"
            ))
            
            success_count += 1
            
        except ValueError as e:
            # 处理文件验证错误（文件大小、类型等）
            error_message = str(e)
            logger.warning(f"文件验证失败 {file.filename}: {error_message}")
            
            submitted_tasks.append(TaskSubmitResponse(
                task_id="",
                message=f"文件验证失败: {error_message}",
                filename=file.filename,
                status="failed"
            ))
            
            failed_count += 1
            
        except Exception as e:
            # 处理其他未预期的错误
            logger.error(f"提交任务失败 {file.filename}: {e}")
            
            submitted_tasks.append(TaskSubmitResponse(
                task_id="",
                message=f"任务提交失败: {str(e)}",
                filename=file.filename,
                status="failed"
            ))
            
            failed_count += 1
    
    response_data = {
        "submitted_tasks": submitted_tasks,
        "total_count": len(files),
        "success_count": success_count,
        "failed_count": failed_count
    }
    
    logger.info(f"批量提交完成: 总计{len(files)}个文件，成功{success_count}个，失败{failed_count}个")
    
    return UnicodeJSONResponse(content=response_data)

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    获取指定任务的状态和结果
    """
    from app.main import queue_manager
    
    task = queue_manager.get_task_status(task_id)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TASK_NOT_FOUND",
                "message": f"任务未找到: {task_id}"
            }
        )
    
    response_data = {
        "task_id": task.task_id,
        "filename": task.filename,
        "file_size": task.file_size,
        "content_type": task.content_type,
        "status": task.status.value,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "duration_ms": task.duration_ms,
        "result": task.result,
        "error": task.error
    }
    
    return UnicodeJSONResponse(content=response_data)

@router.get("/queue/info", response_model=QueueInfoResponse)
async def get_queue_info(api_key: str = Depends(get_api_key)):
    """
    获取转换队列的状态信息
    """
    from app.main import queue_manager
    queue_info = queue_manager.get_queue_info()
    return UnicodeJSONResponse(content=queue_info)

@router.post("/queue/cleanup")
async def cleanup_old_tasks(
    max_age_hours: int = 24,
    api_key: str = Depends(get_api_key)
):
    """
    清理超过指定时间的已完成任务
    """
    from app.main import queue_manager
    cleaned_count = queue_manager.cleanup_old_tasks(max_age_hours)
    
    response_data = {
        "message": f"成功清理 {cleaned_count} 个过期任务",
        "cleaned_count": cleaned_count,
        "max_age_hours": max_age_hours
    }
    
    logger.info(f"清理过期任务完成: {cleaned_count}个任务被清理")
    
    return UnicodeJSONResponse(content=response_data)

@router.get("/supported-types")
async def get_supported_types(api_key: str = Depends(get_api_key)):
    """
    获取支持的文件类型列表
    """
    response_data = {
        "supported_extensions": parser_registry.get_supported_extensions(),
        "total_count": len(parser_registry.get_supported_extensions())
    }
    return UnicodeJSONResponse(content=response_data)

@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(api_key: str = Depends(get_api_key)):
    """
    获取缓存统计信息
    """
    stats = await cache_manager.get_cache_stats()
    return UnicodeJSONResponse(content=stats)

@router.post("/cache/clear")
async def clear_cache(api_key: str = Depends(get_api_key)):
    """
    清除所有缓存数据
    """
    cleared_count = await cache_manager.clear_cache()
    
    response_data = {
        "message": f"成功清除 {cleared_count} 条缓存记录",
        "cleared_count": cleared_count
    }
    
    logger.info(f"缓存清理完成: {cleared_count}条记录被清除")
    
    return UnicodeJSONResponse(content=response_data) 