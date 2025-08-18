from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .config import settings

security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    获取当前用户信息
    
    Args:
        credentials: HTTP 认证凭据
        
    Returns:
        用户标识符（这里使用 API key 作为用户标识）
    """
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API 密钥"
        )
    
    # 返回用户标识符（这里简单返回 API key）
    # 在实际应用中，可以解析 JWT token 或查询数据库获取用户信息
    return f"user_{credentials.credentials[:8]}"


def get_db_session() -> Session:
    return next(get_db())