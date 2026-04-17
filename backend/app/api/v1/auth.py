# app/api/v1/auth.py
import random
import string

from fastapi import APIRouter, Depends, Header
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_mail, get_session
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.response import success_response
from app.core.auth import create_access_token
from app.core.token_blacklist import token_blacklist
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    """用户登录"""
    # 验证用户名密码并获取用户信息
    user = await AuthService.login(data.username, data.password, session)
    
    # 生成 JWT Token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return success_response(
        data={
            "username": user.username,
            "access_token": access_token,
            "token_type": "bearer"
        },
        msg="登录成功"
    )


@router.get("/code")
async def get_email_code(email: str,
                         mail: FastMail = Depends(get_mail),
                         session : AsyncSession =Depends(get_session)
                         ):
    """获取邮箱验证码"""
    #随机产生六位验证码
    source =string.digits * 6
    code = "".join(random.sample(source,6))
    #创建消息对象
    message = MessageSchema(
        subject="邮箱验证码",
        recipients=[email],
        body=f"您好,您的的验证码是{code}\n\n欢迎访问AI 聊天平台，请勿回复此邮件，请勿转发此邮件，请勿保存此邮件。",
        subtype=MessageType.plain
    )
    await mail.send_message(message)
    # 将邮箱和验证码存入数据库
    response =await AuthService.create_email_code(email,code,session)
    #成功业务层会返回ok
    return success_response(data=response, msg="获取成功")


@router.post("/logout")
async def logout(authorization: str = Header(None)):
    """
    用户登出
    
    将 Token 加入黑名单,使其立即失效。
    
    前端应该:
    1. 调用此接口(可选,用于服务端记录)
    2. 删除本地存储的 Token (localStorage/sessionStorage)
    3. 清除认证相关的状态
    4. 跳转到登录页
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        # 将 Token 加入黑名单
        token_blacklist.add_token(token, expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return success_response(msg="登出成功")


# 注册
@router.post("/register")
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """用户注册"""
    response = await AuthService.register(data.username, data.password, data.email, data.code, session)
    return success_response(data=response, msg="注册成功")