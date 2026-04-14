# app/api/v1/auth.py
from fastapi import APIRouter
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(data: LoginRequest):
    """用户登录"""
    response = AuthService.login(data.username, data.password)
    return success_response(data=response, msg="登录成功")
