from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.settings import DB_URI

engine = create_async_engine(
    DB_URI,
    echo=True,# 是否打印sql
    future=True,# 是否使用异步模式
    pool_pre_ping=True, # 检测数据库连接是否断开
    pool_recycle=3600, # 连接池中连接最大空闲时间(回收时间)
    pool_timeout=30, # 连接池中连接最大等待时间(超时时间)
    pool_size=10,  # 连接池大小
    max_overflow=20,# 连接池中连接最大数量
)


AsyncSessionMaker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False,
)