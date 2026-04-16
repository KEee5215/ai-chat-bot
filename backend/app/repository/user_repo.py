from datetime import timedelta, datetime

from app.models.user import EmailCode, User
from sqlalchemy import select, exists, delete
from sqlalchemy.ext.asyncio import AsyncSession



class EmailCodeRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def create(self,email: str,code: str) -> EmailCode:
        # 先删除该邮箱的旧验证码
        delete_stmt = delete(EmailCode).where(EmailCode.email == email)
        await self.session.execute(delete_stmt)

        # 再创建新的验证码
        expire_time = datetime.now() + timedelta(minutes=5)
        email_code = EmailCode(email=email, code=code, expire_time=expire_time)
        self.session.add(email_code)
        await self.session.flush()
        return email_code

    async def check_email_code(self,email: str,code: str) -> bool:
        # 按创建时间降序排列,获取最新的验证码
        stmt = select(EmailCode).where(EmailCode.email == email).order_by(EmailCode.id.desc())
        result = await self.session.execute(stmt)
        email_code: EmailCode | None = result.scalars().first()
        
        if not email_code:
            return False
        
        if datetime.now() > email_code.expire_time:
            return False
        
        if email_code.code != code:
            return False

        return True

# 用户操作数据库
class UserRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def get_by_email(self,email: str) -> User | None:
        """通过邮箱查询用户信息"""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user: User | None = result.scalars().first()
        return user
        # 邮箱是否存在
    async def email_is_exist(self,email: str) -> bool:
        """邮箱是否存在 - 使用 EXISTS 查询更高效"""
        stmt = select(exists().where(User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self,username: str,email: str,password: str) -> User:
        """创建用户"""
        user = User(username=username, email=email, password=password)
        self.session.add(user)
        await self.session.flush()
        return user
