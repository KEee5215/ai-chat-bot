# app/services/auth_service.py
import time

from app.exceptions import BusinessException
from app.models.user import verify_password
from app.repository.user_repo import EmailCodeRepository, UserRepository


class AuthService:
    """认证服务"""

    @staticmethod
    async def login(username: str, password: str, session) -> dict:
        """
        登录业务逻辑 - 验证用户名密码
        
        Args:
            username: 用户名
            password: 密码
            session: 数据库会话
        
        Returns:
            用户对象
        
        Raises:
            BusinessException: 用户名或密码错误
        """
        # user_repo = UserRepository(session)
        
        # 通过用户名查询用户(也可以改为邮箱登录)
        from sqlalchemy import select
        from app.models.user import User
        
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise BusinessException(code=401, message="用户名或密码错误")
        
        # 验证密码
        if not verify_password(password, user.password):
            raise BusinessException(code=401, message="用户名或密码错误")
        
        return user

        ## 将邮箱和验证码存入数据库
    @staticmethod
    async  def create_email_code(email,code,session):
        email_code_repo = EmailCodeRepository(session)
        await email_code_repo.create(str(email),code)
        return "ok"



    @staticmethod
    async def register(username, password, email, code, session):
        email_code_repo = EmailCodeRepository(session)#获取邮箱验证码数据库的会话
        user_repo = UserRepository(session) #获取操作用户数据库的会话
        # 该邮箱是否已经存在
        if await user_repo.email_is_exist(email):
            raise BusinessException(code=400,message="该邮箱已被使用")
        if await email_code_repo.check_email_code(email,code):
            # 创建用户
            await user_repo.create(username, email, password)
            return "ok"
        else:
            raise BusinessException(code=400,message="验证码错误")

