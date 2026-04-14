# app/schemas/auth.py
from pydantic import BaseModel ,Field
from typing import Annotated


class LoginRequest(BaseModel):
    """登录请求"""
    username: Annotated[str, Field(..., min_length=6, max_length=20,description="用户名")]# 这里使用Annotated指定字段的属性
    password: Annotated[str, Field(..., min_length=6, max_length=20,description="密码")]# Field第一个参数是不能省略,


class LoginResponse(BaseModel):
    """登录响应"""
    user_id: Annotated[str, ...]
    username: Annotated[str, ...]
    token: Annotated[str, ...]
