from app.core.mail import create_mail_instance
from models import  AsyncSessionMaker
from fastapi_mail import FastMail
async def get_session():
    session = AsyncSessionMaker()
    try:
        yield session
    finally:
        await session.close()


def get_mail() -> FastMail:
    return create_mail_instance()