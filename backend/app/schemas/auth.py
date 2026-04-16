# app/schemas/auth.py
from pydantic import BaseModel, Field, model_validator
from typing import Annotated

usernameStr = Annotated[str, Field(..., min_length=6, max_length=20,description="用户名")]
passwordStr = Annotated[str, Field(..., min_length=6, max_length=20,description="密码")]
emailStr = Annotated[str, Field(..., min_length=6, max_length=20,description="邮箱")]

class LoginRequest(BaseModel):
    """登录请求"""
    username: usernameStr# 这里使用Annotated指定字段的属性
    password:passwordStr# Field第一个参数是不能省略,


class LoginResponse(BaseModel):
    """登录响应"""
    user_id: Annotated[str, ...]
    username: Annotated[str, ...]
    token: Annotated[str, ...]


# 注册接收参数schema
class RegisterRequest(BaseModel):
    """注册请求"""
    username: usernameStr
    password: passwordStr
    email: emailStr
    code: Annotated[str, Field(..., min_length=6, max_length=6,description="验证码")]
    confirm_password: passwordStr

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("密码不一致")
        return self

class UserCreateSchema(BaseModel):
    """用户创建参数"""
    username: usernameStr
    password: passwordStr
    email: emailStr

