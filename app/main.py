from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
import sys
import json
from pathlib import Path
import asyncio

from app.config import config
from app.routers import convert
from app.queue_manager import ConversionQueueManager
from app.cache import init_cache, close_cache

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level=config.LOG_LEVEL
)

# 记录配置摘要
config.log_config_summary()

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

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    description="将各种文档格式转换为 LLM 理解友好的格式",
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=UnicodeJSONResponse
)

# 添加CORS中间件
if config.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=config.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 创建队列管理器实例
queue_manager = ConversionQueueManager(max_concurrent=config.MAX_CONCURRENT)

# 包含路由
app.include_router(convert.router, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"正在启动 {config.APP_NAME}...")
    
    # 初始化缓存管理器
    await init_cache()
    
    # 启动队列管理器
    await queue_manager.start_worker()
    logger.info(f"队列管理器已启动，支持最多{config.MAX_CONCURRENT}个并发文档转换")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"正在关闭 {config.APP_NAME}...")
    
    # 优雅关闭队列管理器
    await queue_manager.shutdown()
    
    # 关闭缓存管理器
    await close_cache()
    
    # 清理过期任务
    cleaned_count = queue_manager.cleanup_old_tasks(max_age_hours=config.QUEUE_CLEANUP_HOURS)
    if cleaned_count > 0:
        logger.info(f"关闭时清理了 {cleaned_count} 个过期任务")

@app.get("/v1/health")
async def health_check(response: Response):
    """健康检查端点 - 允许所有来源访问"""
    from app.vision import vision_client
    from app.cache import cache_manager
    
    # 设置 CORS 头，允许所有来源访问健康检查端点
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    # 基础服务状态
    health_status = {
        "status": "UP",
        "service": "file2markdown",
        "version": config.APP_VERSION,
        "components": {
            "api": {"status": "UP"},
            "parsers": {"status": "UP"},
            "ocr": {"status": "UP"},
            "queue": {
                "status": "UP",
                "info": queue_manager.get_queue_info()
            },
            "cache": {
                "status": "UP" if cache_manager.enabled else "DISABLED",
                "enabled": cache_manager.enabled
            }
        }
    }
    
    # 检查视觉模型状态
    if vision_client is not None:
        health_status["components"]["vision"] = {
            "status": "UP",
            "configured": True
        }
    elif config.is_vision_enabled():
        health_status["components"]["vision"] = {
            "status": "DOWN",
            "configured": True,
            "error": "初始化失败"
        }
    else:
        health_status["components"]["vision"] = {
            "status": "DISABLED",
            "configured": False,
            "message": "未配置视觉API密钥"
        }
    
    return health_status

@app.options("/v1/health")
async def health_check_options(response: Response):
    """健康检查端点的 OPTIONS 预检请求处理"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"message": "OK"}

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": config.APP_NAME, 
        "version": config.APP_VERSION,
        "features": {
            "single_file_conversion": "支持单文件同步转换",
            "batch_conversion": "支持批量异步转换（队列模式）",
            "max_concurrent": queue_manager.max_concurrent,
            "queue_info": queue_manager.get_queue_info()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    ) 