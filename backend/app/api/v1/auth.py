# app/api/v1/auth.py
import random
import string

from fastapi import APIRouter, Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_mail, get_session
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(data: LoginRequest):
    """用户登录"""
    response = AuthService.login(data.username, data.password)
    return success_response(data=response, msg="登录成功")


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
