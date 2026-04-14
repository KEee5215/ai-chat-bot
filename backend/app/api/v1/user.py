# app/api/v1/users.py
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.annotation import Annotated

from app.dependencies import get_session
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.userSchamaOut import UserSchemaOut
from app.services.user_service import UserService
from app.utils.response import success_response
from app.utils import response


router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/")
async def get_users(page: int = 1, page_size: int = 10):
    """ 分页查询,使用查询参数传参"""
    data = {
        "page": page,
        "pageSize": page_size
    }
    return success_response(data=data)



@router.get("/{user_id}")
async def get_user(user_id: int, session: AsyncSession= Depends(get_session)):
    """根据ID获取用户信息"""
    user_data = await UserService.get_user(user_id, session)
    if not user_data:
        return response.error_response(code=404, msg="用户不存在")
    return response.success_response(data=user_data)



@router.post("/add")
async def add_user(data: UserResponse, session: AsyncSession= Depends(get_session)):
    """添加用户"""
    new_user = await UserService.add_user(data, session)
    return response.success_response(data=UserSchemaOut.model_validate(new_user))

