from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# 初始化安全方案
security = HTTPBearer()

def get_api_keys() -> list[str]:
    """获取有效的API Keys列表"""
    keys_str = os.getenv("AGENT_API_KEYS", "")
    if not keys_str:
        # 开发环境默认key
        return ["dev-test-key-123"]
    return [key.strip() for key in keys_str.split(",") if key.strip()]

async def get_api_key(
    authorization: Optional[str] = Header(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> str:
    """验证API Key依赖注入函数"""
    api_keys = get_api_keys()
    
    # 尝试从Authorization header获取
    token = None
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_API_KEY",
                "message": "API Key is required. Please provide it in Authorization header."
            }
        )
    
    if token not in api_keys:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_API_KEY", 
                "message": "Invalid API Key provided."
            }
        )
    
    return token 