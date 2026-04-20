from app.core.mail import create_mail_instance
from models import AsyncSessionMaker, SyncSessionMaker
from fastapi_mail import FastMail
from sqlalchemy.orm import Session
from typing import Generator
async def get_session():
    """异步数据库会话依赖（用于常规API）"""
    session = AsyncSessionMaker()
    try:
        yield session
        await session.commit()  # 请求成功时提交事务
    except Exception:
        await session.rollback()  # 发生异常时回滚
        raise
    finally:
        await session.close()


def get_db() -> Generator[Session, None, None]:
    """同步数据库会话依赖（用于RAG等同步操作）"""
    db = SyncSessionMaker()
    try:
        yield db
        db.commit()  # 请求成功时提交事务
    except Exception:
        db.rollback()  # 发生异常时回滚
        raise
    finally:
        db.close()


def get_mail() -> FastMail:
    return create_mail_instance()