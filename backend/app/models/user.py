from datetime import datetime

from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import  List

from . import Base

class User(Base):
    """用户表"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), unique=True,index= True)
    password: Mapped[str] = mapped_column(String(200) )
    user_extension: Mapped["UserExtension"] = relationship(back_populates="User",uselist= False)
    articles: Mapped[List["Article"]] = relationship(back_populates="author")

class UserExtension(Base):
    """用户扩展表"""
    __tablename__ = "user_extension"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), unique=True) # 外键
    phone: Mapped[str] = mapped_column(String(20))
    User: Mapped["User"] = relationship(back_populates="user_extension")# 反向关系
