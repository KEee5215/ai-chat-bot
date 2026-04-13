# app/api/v1/users.py
from fastapi import APIRouter
from app.services.user_service import UserService
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    data = UserService.get_user(user_id)
    return success_response(data=data)
