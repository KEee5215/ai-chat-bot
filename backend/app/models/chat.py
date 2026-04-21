from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean, Table, Column
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
    rag_messages: Mapped[List["RAGChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(
        back_populates="sessions",
        secondary="session_documents"
    )

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


# 文档元信息表结构
class Document(Base):
    """文档元数据表"""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="文档ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True, comment="关联用户ID")
    original_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名,如'报告.pdf'")
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="对象存储路径,如'/uploads/2026/04/xxx.pdf'")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小(字节)")
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件后缀,如'pdf','docx','txt'")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True, comment="MIME类型,如'application/pdf'")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="上传时间")
    
    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="documents")
    sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="documents",
        secondary="session_documents"
    )


# 文档与会话关系表, 中间表
# 会话-文档关联表(多对多)
session_documents = Table(
    "session_documents",
    Base.metadata,
    Column("session_id", Integer, ForeignKey("chat_session.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True)
)


class RAGChatMessage(Base):
    """RAG 对话记录表 - 专门存储 RAG 问答历史"""
    __tablename__ = "rag_chat_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_session.id"), nullable=False, index=True)
    user_question: Mapped[str] = mapped_column(Text, nullable=False, comment="用户问题")
    ai_answer: Mapped[str] = mapped_column(Text, nullable=False, comment="AI回答")
    document_ids: Mapped[str] = mapped_column(String(500), nullable=True, comment="检索的文档ID列表，JSON格式")
    source_info: Mapped[str] = mapped_column(Text, nullable=True, comment="来源文档信息，JSON格式")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    session: Mapped["ChatSession"] = relationship(back_populates="rag_messages")

    def __repr__(self):
        return f"<RAGChatMessage(id={self.id}, session_id={self.session_id})>"
