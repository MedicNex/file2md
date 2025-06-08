from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
import sys
import json
from dotenv import load_dotenv
from pathlib import Path
import asyncio

from app.routers import convert
from app.queue_manager import queue_manager

# 自动加载.env文件，指定正确路径
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

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
    title="MedicNex File2Markdown Service",
    description="将各种文档格式转换为Markdown的微服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=UnicodeJSONResponse
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(convert.router, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("正在启动 MedicNex File2Markdown Service...")
    
    # 启动队列管理器
    await queue_manager.start_worker()
    logger.info("队列管理器已启动，支持最多5个并发文档转换")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭 MedicNex File2Markdown Service...")
    
    # 清理过期任务
    cleaned_count = queue_manager.cleanup_old_tasks(max_age_hours=1)
    if cleaned_count > 0:
        logger.info(f"关闭时清理了 {cleaned_count} 个过期任务")

@app.get("/v1/health")
async def health_check():
    """健康检查端点"""
    from app.vision import vision_client, VISION_API_KEY, VISION_API_BASE, VISION_MODEL
    
    # 基础服务状态
    health_status = {
        "status": "UP",
        "service": "file2markdown",
        "version": "1.0.0",
        "components": {
            "api": {"status": "UP"},
            "parsers": {"status": "UP"},
            "ocr": {"status": "UP"},
            "queue": {
                "status": "UP",
                "info": queue_manager.get_queue_info()
            }
        }
    }
    
    # 检查视觉模型状态
    if vision_client is not None:
        health_status["components"]["vision"] = {
            "status": "UP",
            "api_base": VISION_API_BASE,
            "model": VISION_MODEL,
            "configured": True
        }
    elif VISION_API_KEY:
        health_status["components"]["vision"] = {
            "status": "DOWN",
            "api_base": VISION_API_BASE,
            "model": VISION_MODEL,
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

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MedicNex File2Markdown Service", 
        "version": "1.0.0",
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
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=True
    ) 