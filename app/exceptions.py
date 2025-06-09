"""
自定义异常类型

提供更明确的错误分类和处理
"""
from typing import Optional, Dict, Any


class File2MDError(Exception):
    """File2MD服务的基础异常类"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于API响应"""
        return {
            "code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(File2MDError):
    """配置相关错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class FileProcessingError(File2MDError):
    """文件处理相关错误"""
    
    def __init__(self, message: str, filename: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if filename:
            error_details["filename"] = filename
        super().__init__(message, "FILE_PROCESSING_ERROR", error_details)


class UnsupportedFileTypeError(FileProcessingError):
    """不支持的文件类型错误"""
    
    def __init__(self, file_extension: str, supported_types: list, filename: Optional[str] = None):
        message = f"不支持的文件类型: {file_extension}"
        details = {
            "file_extension": file_extension,
            "supported_types": supported_types
        }
        super().__init__(message, filename, details)
        self.error_code = "UNSUPPORTED_FILE_TYPE"


class FileSizeError(FileProcessingError):
    """文件大小错误"""
    
    def __init__(self, file_size: int, max_size: int, filename: Optional[str] = None):
        message = f"文件大小超出限制: {file_size} bytes (最大: {max_size} bytes)"
        details = {
            "file_size": file_size,
            "max_size": max_size
        }
        super().__init__(message, filename, details)
        self.error_code = "FILE_SIZE_EXCEEDED"


class ParseError(FileProcessingError):
    """文件解析错误"""
    
    def __init__(self, message: str, filename: Optional[str] = None, parser_type: Optional[str] = None):
        details = {}
        if parser_type:
            details["parser_type"] = parser_type
        super().__init__(message, filename, details)
        self.error_code = "PARSE_ERROR"


class QueueError(File2MDError):
    """队列相关错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "QUEUE_ERROR", details)


class TaskNotFoundError(QueueError):
    """任务未找到错误"""
    
    def __init__(self, task_id: str):
        message = f"任务未找到: {task_id}"
        details = {"task_id": task_id}
        super().__init__(message, details)
        self.error_code = "TASK_NOT_FOUND"


class QueueFullError(QueueError):
    """队列已满错误"""
    
    def __init__(self, current_size: int, max_size: int):
        message = f"队列已满，无法添加新任务 (当前: {current_size}, 最大: {max_size})"
        details = {
            "current_size": current_size,
            "max_size": max_size
        }
        super().__init__(message, details)
        self.error_code = "QUEUE_FULL"


class AuthenticationError(File2MDError):
    """认证相关错误"""
    
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class RateLimitError(File2MDError):
    """速率限制错误"""
    
    def __init__(self, message: str = "请求频率过高", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class ExternalServiceError(File2MDError):
    """外部服务错误"""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        error_details["service_name"] = service_name
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", error_details)


class VisionAPIError(ExternalServiceError):
    """视觉API错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("Vision API", message, details)
        self.error_code = "VISION_API_ERROR"


class VisionAPIConnectionError(VisionAPIError):
    """视觉API连接错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = "VISION_API_CONNECTION_ERROR"


class VisionAPIRateLimitError(VisionAPIError):
    """视觉API速率限制错误"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, details)
        self.error_code = "VISION_API_RATE_LIMIT"


class OCRError(ExternalServiceError):
    """OCR处理错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("OCR", message, details)
        self.error_code = "OCR_ERROR"


class ResourceCleanupError(File2MDError):
    """资源清理错误"""
    
    def __init__(self, resource_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        error_details["resource_type"] = resource_type
        super().__init__(message, "RESOURCE_CLEANUP_ERROR", error_details) 