from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.token_blacklist import token_blacklist

# HTTP Bearer Token 安全方案
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Access Token
    
    Args:
        data: 要编码的数据(通常包含用户ID等信息)
        expires_delta: 可选的过期时间增量,默认使用 ACCESS_TOKEN_EXPIRE_MINUTES
    
    Returns:
        编码后的 JWT token 字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 编码生成 token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    验证 JWT Token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        解码后的 payload 数据
    
    Raises:
        InvalidTokenError: Token 无效或已过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError as e:
        raise InvalidTokenError(f"Token 验证失败: {str(e)}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI 依赖注入:获取当前登录用户信息
    
    使用方式:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            ...
    
    Args:
        credentials: HTTP Bearer 认证信息
    
    Returns:
        包含用户信息的字典 {"user_id": int, "username": str}
    
    Raises:
        HTTPException: 未认证或 Token 无效
    """
    token = credentials.credentials
    
    # 检查 Token 是否在黑名单中(已登出)
    if token_blacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已失效,请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": int(user_id),
            "username": username
        }
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    current_user: dict = Depends(get_current_user)
) -> int:
    """
    FastAPI 依赖注入:仅获取当前用户 ID
    
    使用方式:
        @router.get("/protected")
        async def protected_route(user_id: int = Depends(get_current_user_id)):
            ...
    """
    return current_user["user_id"]
