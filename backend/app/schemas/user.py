# app/schemas/auth.py
from pydantic import BaseModel


class UserResponse(BaseModel):
    """用户信息响应"""
    user_id: str
    user_name: str
