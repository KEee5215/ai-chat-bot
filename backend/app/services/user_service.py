# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.userSchamaOut import UserSchemaOut


class UserService:
    """用户服务"""

    @staticmethod
    async def get_user(user_id: int, session: AsyncSession):
        """
        根据id获取用户信息
        """
        user_info = await session.get(User, user_id)
        if not user_info:
            return None
        # 使用 Pydantic 模型验证并过滤字段(自动排除 password)
        user_data = UserSchemaOut.model_validate(user_info)

        return user_data

    @staticmethod
    async def add_user(data: UserResponse, session: AsyncSession):
        """
        添加用户
        """
        # 创建用户对象
        new_user = User(username=data.username, password=data.password, email=data.email)
        session.add(new_user)
        # 提交事务
        await session.commit()
        # 刷新以获取自增 ID
        await session.refresh(new_user)

        return new_user

