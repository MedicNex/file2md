from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
import sys
import json

from app.routers import convert

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

@app.get("/v1/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "file2markdown"}

@app.get("/")
async def root():
    """根路径"""
    return {"message": "MedicNex File2Markdown Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=True
    ) 