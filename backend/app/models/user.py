from datetime import datetime

from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from pwdlib import PasswordHash

#密码加密第三方库



from . import Base

password_hash = PasswordHash.recommended()

# 密码验证
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# 密码加密
def get_password_hash(password):
    return password_hash.hash(password)




class User(Base):
    """用户表"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    _password: Mapped[str] = mapped_column(String(200), nullable=False)
    user_extension: Mapped["UserExtension"] = relationship(back_populates="user", uselist=False)

    chat_sessions: Mapped[List["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(back_populates="user")

    def __init__(self, *args, **kwargs):
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = get_password_hash(value)

class EmailCode(Base):
    """邮箱验证码表"""
    __tablename__ = "email_code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10))
    expire_time: Mapped[datetime] = mapped_column(DateTime)


class UserExtension(Base):
    """用户扩展表"""
    __tablename__ = "user_extension"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), unique=True)  # 外键
    phone: Mapped[str] = mapped_column(String(20))
    user: Mapped["User"] = relationship(back_populates="user_extension")  # 反向关系
