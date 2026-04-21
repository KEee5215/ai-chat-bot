from typing import List

from pydantic import BaseModel, Field


class SessionIn(BaseModel):
    """会话输入参数"""
    title: str = Field(..., description="会话标题") # 用户输入的输入的标题



class ChatIn(BaseModel):
    """聊天输入参数"""
    message: str = Field(..., description="用户消息") #新消息
    session_id: int = Field(None, description="会话ID") #会话id,必须



class RAGQueryRequest(BaseModel):
    """RAG 查询请求"""
    document_ids: List[int]  # 要检索的文档ID列表
    question: str  # 用户问题
