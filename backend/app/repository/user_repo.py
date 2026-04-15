from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import EmailCode


class EmailCodeRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    # 创建
    async def create(self,email: str,code: str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            # ✅ 正确 - 设置所有必填字段
            expire_time = datetime.now() + timedelta(minutes=5)
            email_code = EmailCode(email=email, code=code, expire_time=expire_time)

            self.session.add(email_code)
            return email_code

    # 验证码验证
    async def check_email_code(self,email: str,code: str) -> bool:
        async with self.session.begin():
            stmt = select(EmailCode).where(EmailCode.email == email)
            result = await self.session.execute(stmt)
            email_code: EmailCode | None = result.scalar_one_or_none()
            # 是否存在
            if not email_code:
                return False
            # 是否过期
            if datetime.now() > email_code.expire_time:
                return False
            # 验证码是否一致
            if email_code.code != code:
                return False

            return True

