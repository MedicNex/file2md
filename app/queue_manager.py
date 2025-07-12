import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
from loguru import logger
from fastapi import UploadFile
import tempfile
import os
from pathlib import Path

from app.parsers.registry import parser_registry
from app.cache import cache_manager


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConversionTask:
    """转换任务数据类"""
    task_id: str
    filename: str
    file_size: int
    content_type: str
    temp_file_path: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class ConversionQueueManager:
    """
    文档转换队列管理器
    
    提供异步队列处理和优雅关闭功能
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks: Dict[str, ConversionTask] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self._worker_started = False
        self._worker_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start_worker(self):
        """启动队列处理工作器"""
        if not self._worker_started:
            self._worker_started = True
            self._worker_task = asyncio.create_task(self._queue_worker())
            logger.info(f"队列管理器已启动，最大并发数: {self.max_concurrent}")
    
    async def shutdown(self):
        """优雅关闭队列管理器"""
        logger.info("开始关闭队列管理器...")
        
        # 设置关闭标志
        self._shutdown_event.set()
        
        # 取消工作器任务
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                logger.info("队列工作器已取消")
        
        # 取消所有活跃任务
        if self.active_tasks:
            logger.info(f"取消 {len(self.active_tasks)} 个活跃任务")
            for task_id, task in self.active_tasks.items():
                if not task.done():
                    task.cancel()
            
            # 等待所有任务完成或被取消
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        # 清理资源
        await self._cleanup_resources()
        
        logger.info("队列管理器已关闭")
    
    async def _cleanup_resources(self):
        """清理所有资源"""
        for task in self.tasks.values():
            if task.temp_file_path and os.path.exists(task.temp_file_path):
                try:
                    os.unlink(task.temp_file_path)
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {task.temp_file_path}: {e}")
    
    async def _queue_worker(self):
        """队列工作器，持续处理队列中的任务"""
        logger.info("队列工作器已启动")
        
        try:
            while not self._shutdown_event.is_set():
                try:
                    # 使用超时等待任务，以便定期检查关闭信号
                    task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                    
                    if task_id in self.tasks:
                        # 创建处理任务的协程
                        task_coroutine = self._process_task(task_id)
                        self.active_tasks[task_id] = asyncio.create_task(task_coroutine)
                    
                    # 标记队列任务完成
                    self.queue.task_done()
                    
                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环检查关闭信号
                    continue
                except asyncio.CancelledError:
                    logger.info("队列工作器收到取消信号")
                    break
                except Exception as e:
                    logger.error(f"队列工作器处理异常: {e}")
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("队列工作器被取消")
        finally:
            logger.info("队列工作器已退出")
    
    async def _process_task(self, task_id: str):
        """处理单个转换任务"""
        async with self.semaphore:  # 控制并发数量
            task = self.tasks.get(task_id)
            if not task:
                return
                
            try:
                # 更新任务状态
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.now()
                
                logger.info(f"开始处理任务: {task.filename} (ID: {task_id})")
                
                # 读取文件内容用于缓存检查
                with open(task.temp_file_path, 'rb') as f:
                    file_content = f.read()
                
                # 检查缓存
                cached_result = await cache_manager.get_cached_result(file_content)
                if cached_result:
                    # 使用缓存结果
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    task.result = cached_result['content']
                    task.duration_ms = int((task.completed_at - task.started_at).total_seconds() * 1000)
                    
                    logger.info(f"任务从缓存完成: {task.filename} (ID: {task_id}), 耗时: {task.duration_ms}ms (缓存命中)")
                    return
                
                # 获取文件扩展名
                file_extension = Path(task.filename).suffix.lower()
                
                # 获取解析器
                parser_class = parser_registry.get_parser(file_extension)
                if parser_class is None:
                    raise ValueError(f"未找到文件类型 {file_extension} 的解析器")
                parser_instance = parser_class()
                
                # 执行文件转换
                start_time = datetime.now()
                markdown_content = await parser_instance.parse(task.temp_file_path)
                end_time = datetime.now()
                
                # 计算处理时间
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # 缓存结果
                await cache_manager.cache_result(
                    file_content=file_content,
                    filename=task.filename,
                    markdown_content=markdown_content,
                    file_size=task.file_size,
                    duration_ms=duration_ms,
                    content_type=task.content_type
                )
                
                # 更新任务结果
                task.status = TaskStatus.COMPLETED
                task.completed_at = end_time
                task.result = markdown_content
                task.duration_ms = duration_ms
                
                logger.info(f"任务处理完成: {task.filename} (ID: {task_id}), 耗时: {duration_ms}ms")
                
                # 清理解析器临时文件
                try:
                    parser_instance.cleanup()
                except Exception as cleanup_error:
                    logger.warning(f"解析器清理失败 (任务 {task_id}): {cleanup_error}")
                
            except Exception as e:
                # 处理失败
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error = str(e)
                
                logger.error(f"任务处理失败: {task.filename} (ID: {task_id}): {e}")
                
            finally:
                # 清理临时文件
                if task.temp_file_path and os.path.exists(task.temp_file_path):
                    try:
                        os.unlink(task.temp_file_path)
                    except Exception as cleanup_error:
                        logger.warning(f"临时文件清理失败 (任务 {task_id}): {cleanup_error}")
                
                # 从活跃任务中移除
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def submit_task(self, file: UploadFile) -> str:
        """提交文件转换任务到队列"""
        from app.config import config
        
        # 验证文件
        if not file.filename:
            raise ValueError("文件名不能为空")
        
        # 获取文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        
        # 检查是否支持该文件类型
        if not parser_registry.is_supported(file_extension):
            supported_exts = parser_registry.get_supported_extensions()
            raise ValueError(f"不支持的文件类型: {file_extension}, 支持的类型: {supported_exts}")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存上传的文件到临时位置
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name
        
        try:
            # 使用流式读取检查文件大小，避免内存耗尽
            file_size = 0
            content = b""
            chunk_size = 8192  # 8KB 块大小
            
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                
                # 检查是否超过大小限制，避免继续读取和内存耗尽
                if file_size > config.MAX_FILE_SIZE:
                    # 立即关闭并清理临时文件
                    temp_file.close()
                    if os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                        except:
                            pass
                    raise ValueError(
                        f"文件过大: {file_size} bytes，最大允许: {config.MAX_FILE_SIZE} bytes "
                        f"({config.MAX_FILE_SIZE // 1024 // 1024} MB)"
                    )
                content += chunk
            
            if file_size == 0:
                temp_file.close()
                if os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                raise ValueError("文件为空")
            
            # 写入文件内容
            temp_file.write(content)
            temp_file.close()
            
            # 创建任务
            task = ConversionTask(
                task_id=task_id,
                filename=file.filename,
                file_size=file_size,
                content_type=file.content_type or "application/octet-stream",
                temp_file_path=temp_file_path
            )
            
            # 保存任务到字典
            self.tasks[task_id] = task
            
            # 将任务ID加入队列
            await self.queue.put(task_id)
            
            logger.info(f"任务已提交到队列: {file.filename} (ID: {task_id}), 大小: {file_size} bytes")
            
            return task_id
            
        except Exception as e:
            # 如果出错，清理临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise e
    
    def get_task_status(self, task_id: str) -> Optional[ConversionTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列状态信息"""
        pending_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING)
        processing_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PROCESSING)
        completed_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        failed_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
        
        return {
            "max_concurrent": self.max_concurrent,
            "queue_size": self.queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "total_tasks": len(self.tasks),
            "pending_count": pending_count,
            "processing_count": processing_count,
            "completed_count": completed_count,
            "failed_count": failed_count
        }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理超过指定时间的已完成任务"""
        current_time = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                if task.completed_at and (current_time - task.completed_at).total_seconds() > max_age_hours * 3600:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            logger.info(f"清理过期任务: {task_id}")
        
        return len(to_remove) 