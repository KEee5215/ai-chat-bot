from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

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


AsyncSessionMaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 定义命名约定的Base类
class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            # 索引 index
            "ix": "ix_%(column_0_label)s",
            # 唯一索引 unique
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            # 检查约束  check
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            # 外键约束  foreign key
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            # 主键约束  primary key
            "pk": "pk_%(table_name)s",
        }
    )

# 在文件底部导入所有模型，确保 Base 已完全定义
from . import user
from . import article
from . import chat