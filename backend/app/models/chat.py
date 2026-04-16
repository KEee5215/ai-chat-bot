from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from . import Base


class ChatSession(Base):
    """聊天会话表 - 每个用户可以有多个会话"""
    __tablename__ = "chat_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), default="新对话")  # 会话标题
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)  # 软删除标记
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    user: Mapped["User"] = relationship(back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class ChatMessage(Base):
    """聊天消息表 - 存储对话历史"""
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_session.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 消息内容
    token_count: Mapped[int] = mapped_column(Integer, default=0)  # token 数量(可选)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    session: Mapped["ChatSession"] = relationship(back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"
