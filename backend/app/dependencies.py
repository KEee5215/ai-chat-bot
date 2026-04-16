from app.core.mail import create_mail_instance
from models import  AsyncSessionMaker
from fastapi_mail import FastMail
async def get_session():
    session = AsyncSessionMaker()
    try:
        yield session
        await session.commit()  # 请求成功时提交事务
    except Exception:
        await session.rollback()  # 发生异常时回滚
        raise
    finally:
        await session.close()


def get_mail() -> FastMail:
    return create_mail_instance()