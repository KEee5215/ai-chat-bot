from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


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


def get_current_user_id(token: str) -> int:
    """
    从 Token 中获取当前用户 ID
    
    Args:
        token: JWT token 字符串
    
    Returns:
        用户 ID
    
    Raises:
        InvalidTokenError: Token 无效或已过期
    """
    payload = verify_token(token)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError("Token 中缺少用户ID")
    return user_id
