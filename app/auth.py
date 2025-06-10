from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.config import config

# 初始化安全方案
security = HTTPBearer(auto_error=False)

def get_api_keys() -> list[str]:
    """获取有效的API Keys列表"""
    # 优先使用新的配置系统
    if config.API_KEY:
        return [config.API_KEY]

async def get_api_key(
    authorization: Optional[str] = Header(None, alias="X-API-Key"),
    auth_header: Optional[str] = Header(None, alias="Authorization"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """验证API Key依赖注入函数"""
    
    # 强制启用API Key验证 - 无论配置如何都需要验证
    api_keys = get_api_keys()
    
    # 如果没有配置任何API Key，则拒绝所有请求
    if not api_keys:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "API_KEY_NOT_CONFIGURED",
                "message": "服务器未配置API密钥，请联系管理员配置API_KEY环境变量。"
            }
        )
    
    # 尝试从多个地方获取token
    token = None
    
    # 1. 从X-API-Key header获取
    if authorization:
        token = authorization
    # 2. 从Authorization header获取
    elif auth_header:
        parts = auth_header.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = auth_header
    # 3. 从HTTPBearer获取
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_API_KEY",
                "message": "需要提供API密钥。请在请求头中包含X-API-Key或Authorization字段。"
            }
        )
    
    # 验证token是否在有效的API Keys列表中
    if token not in api_keys:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_API_KEY", 
                "message": "提供的API密钥无效，请检查后重试。"
            }
        )
    
    return token 