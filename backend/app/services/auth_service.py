# app/services/auth_service.py
import time

from app.exceptions import BusinessException
from app.repository.user_repo import EmailCodeRepository, UserRepository


class AuthService:
    """认证服务"""

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        登录业务逻辑
        TODO: 这里应该验证用户名密码，查询数据库等
        """
        timestamp = int(time.time())
        return {
            "user_id": timestamp,
            "username": username,
            "token": "123456"  # TODO: 生成真实的 JWT token
        }

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

