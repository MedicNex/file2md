"""
配置管理模块

集中管理应用的所有配置项，避免重复的环境变量加载
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

# 确保只加载一次.env文件
_env_loaded = False


def load_environment():
    """加载环境变量配置"""
    global _env_loaded
    if _env_loaded:
        return
    
    # 自动加载.env文件，指定正确路径
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"已加载环境配置文件: {env_path}")
    else:
        logger.info("未找到.env文件，使用系统环境变量")
    
    _env_loaded = True


# 确保配置被加载
load_environment()


class Config:
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "MedicNex File2Markdown Service"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 队列配置
    MAX_CONCURRENT: int = int(os.getenv("MAX_CONCURRENT", "5"))
    QUEUE_CLEANUP_HOURS: int = int(os.getenv("QUEUE_CLEANUP_HOURS", "24"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_DETAILED_LOGGING: bool = os.getenv("ENABLE_DETAILED_LOGGING", "false").lower() == "true"
    MAX_LOG_CONTENT_LENGTH: int = int(os.getenv("MAX_LOG_CONTENT_LENGTH", "500"))
    
    # 视觉API配置
    VISION_API_KEY: Optional[str] = os.getenv("VISION_API_KEY")
    VISION_API_BASE: str = os.getenv("VISION_API_BASE", "https://api.openai.com/v1")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gpt-4o-mini")
    VISION_MAX_RETRIES: int = int(os.getenv("VISION_MAX_RETRIES", "3"))
    VISION_RETRY_DELAY: float = float(os.getenv("VISION_RETRY_DELAY", "1.0"))
    VISION_BACKOFF_FACTOR: float = float(os.getenv("VISION_BACKOFF_FACTOR", "2.0"))
    
    # 兼容旧的OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # API安全配置
    API_KEY: Optional[str] = os.getenv("API_KEY")
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "true").lower() == "true"
    
    # 文件处理配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # MB to bytes
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp")
    
    # 文本文件处理配置
    MAX_TEXT_LINES: int = int(os.getenv("MAX_TEXT_LINES", "50000"))  # 最大行数
    MAX_TEXT_CHARS: int = int(os.getenv("MAX_TEXT_CHARS", "10000000"))  # 最大字符数 (约10MB文本)
    TEXT_CHUNK_SIZE: int = int(os.getenv("TEXT_CHUNK_SIZE", "1048576"))  # 文本块大小 (1MB)
    
    # CORS配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    @classmethod
    def get_vision_api_key(cls) -> Optional[str]:
        """获取视觉API密钥，优先使用专用密钥"""
        return cls.VISION_API_KEY or cls.OPENAI_API_KEY
    
    @classmethod
    def is_vision_enabled(cls) -> bool:
        """检查是否启用了视觉API"""
        return cls.get_vision_api_key() is not None
    
    @classmethod
    def validate_config(cls) -> None:
        """验证关键配置项"""
        errors = []
        
        if cls.REQUIRE_API_KEY and not cls.API_KEY:
            errors.append("需要API_KEY但未配置")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append(f"端口号无效: {cls.PORT}")
        
        if cls.MAX_CONCURRENT < 1:
            errors.append(f"最大并发数无效: {cls.MAX_CONCURRENT}")
        
        if cls.MAX_FILE_SIZE < 1024:  # 最小1KB
            errors.append(f"最大文件大小无效: {cls.MAX_FILE_SIZE}")
        
        if cls.MAX_TEXT_LINES < 1:
            errors.append(f"最大文本行数无效: {cls.MAX_TEXT_LINES}")
        
        if cls.MAX_TEXT_CHARS < 1024:  # 最小1KB文本
            errors.append(f"最大文本字符数无效: {cls.MAX_TEXT_CHARS}")
        
        if cls.TEXT_CHUNK_SIZE < 1024:  # 最小1KB块
            errors.append(f"文本块大小无效: {cls.TEXT_CHUNK_SIZE}")
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("配置验证通过")
    
    @classmethod
    def log_config_summary(cls) -> None:
        """记录配置摘要"""
        logger.info("=== 应用配置摘要 ===")
        logger.info(f"应用名称: {cls.APP_NAME}")
        logger.info(f"版本: {cls.APP_VERSION}")
        logger.info(f"监听地址: {cls.HOST}:{cls.PORT}")
        logger.info(f"调试模式: {cls.DEBUG}")
        logger.info(f"最大并发: {cls.MAX_CONCURRENT}")
        logger.info(f"日志级别: {cls.LOG_LEVEL}")
        logger.info(f"详细日志: {cls.ENABLE_DETAILED_LOGGING}")
        logger.info(f"最大文件大小: {cls.MAX_FILE_SIZE // 1024 // 1024} MB")
        logger.info(f"最大文本行数: {cls.MAX_TEXT_LINES}")
        logger.info(f"最大文本字符数: {cls.MAX_TEXT_CHARS}")
        logger.info(f"视觉API: {'已启用' if cls.is_vision_enabled() else '未启用'}")
        logger.info(f"API密钥验证: {'必需' if cls.REQUIRE_API_KEY else '可选'}")
        logger.info("==================")


# 全局配置实例
config = Config()

# 在模块加载时验证配置
try:
    config.validate_config()
except ValueError as e:
    logger.error(f"配置加载失败: {e}")
    raise 