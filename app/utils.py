"""
工具模块

包含资源清理、文件处理等通用功能
"""
import os
import asyncio
import aiofiles
import aiofiles.os
from typing import List, Optional, Union
from pathlib import Path
from loguru import logger

from app.exceptions import ResourceCleanupError


class ResourceCleaner:
    """资源清理器"""
    
    def __init__(self):
        self.cleanup_tasks: List[str] = []
    
    def add_file(self, file_path: str) -> None:
        """添加需要清理的文件"""
        if file_path and file_path not in self.cleanup_tasks:
            self.cleanup_tasks.append(file_path)
    
    def add_files(self, file_paths: List[str]) -> None:
        """批量添加需要清理的文件"""
        for file_path in file_paths:
            self.add_file(file_path)
    
    async def cleanup_async(self) -> int:
        """异步清理所有文件"""
        cleaned_count = 0
        errors = []
        
        for file_path in self.cleanup_tasks:
            try:
                if await aiofiles.os.path.exists(file_path):
                    await aiofiles.os.unlink(file_path)
                    cleaned_count += 1
                    logger.debug(f"已清理文件: {file_path}")
            except Exception as e:
                error_msg = f"清理文件失败 {file_path}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        self.cleanup_tasks.clear()
        
        if errors and len(errors) == len(self.cleanup_tasks):
            # 如果所有文件都清理失败，抛出异常
            raise ResourceCleanupError("file", f"所有文件清理失败: {'; '.join(errors)}")
        
        return cleaned_count
    
    def cleanup_sync(self) -> int:
        """同步清理所有文件"""
        cleaned_count = 0
        errors = []
        
        for file_path in self.cleanup_tasks:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    cleaned_count += 1
                    logger.debug(f"已清理文件: {file_path}")
            except Exception as e:
                error_msg = f"清理文件失败 {file_path}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        self.cleanup_tasks.clear()
        
        if errors and len(errors) == len(self.cleanup_tasks):
            # 如果所有文件都清理失败，抛出异常
            raise ResourceCleanupError("file", f"所有文件清理失败: {'; '.join(errors)}")
        
        return cleaned_count
    
    def __len__(self) -> int:
        """返回待清理文件数量"""
        return len(self.cleanup_tasks)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，自动清理"""
        try:
            self.cleanup_sync()
        except Exception as e:
            logger.error(f"上下文管理器清理失败: {e}")


async def safe_file_operation(operation, *args, **kwargs):
    """
    安全的文件操作包装器
    
    Args:
        operation: 要执行的文件操作函数
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        操作结果
        
    Raises:
        FileProcessingError: 文件操作失败
    """
    try:
        if asyncio.iscoroutinefunction(operation):
            return await operation(*args, **kwargs)
        else:
            return operation(*args, **kwargs)
    except FileNotFoundError as e:
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"文件未找到: {e}")
    except PermissionError as e:
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"文件权限不足: {e}")
    except OSError as e:
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"文件系统错误: {e}")
    except Exception as e:
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"文件操作失败: {e}")


async def validate_file_size(file_path: str, max_size: int) -> int:
    """
    验证文件大小
    
    Args:
        file_path: 文件路径
        max_size: 最大允许大小（字节）
        
    Returns:
        文件大小
        
    Raises:
        FileSizeError: 文件大小超出限制
        FileProcessingError: 文件操作失败
    """
    try:
        stat = await aiofiles.os.stat(file_path)
        file_size = stat.st_size
        
        if file_size > max_size:
            from app.exceptions import FileSizeError
            raise FileSizeError(file_size, max_size, Path(file_path).name)
        
        return file_size
    except Exception as e:
        if hasattr(e, 'error_code'):  # 已经是我们的自定义异常
            raise
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"无法获取文件大小: {e}", Path(file_path).name)


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名（小写）
    
    Args:
        filename: 文件名
        
    Returns:
        文件扩展名（包含点号，如 '.txt'）
    """
    return Path(filename).suffix.lower()


def is_safe_filename(filename: str) -> bool:
    """
    检查文件名是否安全
    
    Args:
        filename: 文件名
        
    Returns:
        是否安全
    """
    if not filename or filename in ('.', '..'):
        return False
    
    # 检查危险字符
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in filename for char in dangerous_chars):
        return False
    
    # 检查控制字符
    if any(ord(char) < 32 for char in filename):
        return False
    
    return True


async def create_temp_file_safe(content: Union[str, bytes], suffix: str = "", prefix: str = "file2md_") -> str:
    """
    安全创建临时文件
    
    Args:
        content: 文件内容
        suffix: 文件后缀
        prefix: 文件前缀
        
    Returns:
        临时文件路径
        
    Raises:
        FileProcessingError: 创建失败
    """
    import tempfile
    
    try:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # 写入内容
        if isinstance(content, str):
            async with aiofiles.open(temp_file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
        else:
            async with aiofiles.open(temp_file_path, 'wb') as f:
                await f.write(content)
        
        return temp_file_path
    except Exception as e:
        from app.exceptions import FileProcessingError
        raise FileProcessingError(f"创建临时文件失败: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


async def retry_async(func, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    异步重试装饰器
    
    Args:
        func: 要重试的异步函数
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
        
    Returns:
        函数执行结果
        
    Raises:
        最后一次执行的异常
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"重试 {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                logger.error(f"重试失败，已达到最大重试次数 {max_retries}")
    
    if last_exception is not None:
        raise last_exception
    else:
        raise Exception("重试失败，但未捕获到具体异常") 