# app/api/v1/rag.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.auth import get_current_user_id, get_current_user
from app.dependencies import  get_db
from app.utils import response
from app.schemas.response import ApiResponse
from app.services.rag_service import RAGService
from app.repository.document_repo import DocumentRepository
from app.schemas.chat import RAGQueryRequest
import os
import hashlib
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/rag", tags=["RAG"])

# 文件上传配置
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"pdf", "txt"}  # 目前支持的类型
UPLOAD_BASE_PATH = "./uploads"


# RAG 查询请求模型
class RAGQueryRequest(BaseModel):
    """RAG 查询请求"""
    document_ids: List[int]  # 要检索的文档ID列表
    question: str  # 用户问题


# 文件上传请求模型
class DocumentUploadRequest(BaseModel):
    """文件上传请求（可选关联会话）"""
    session_id: int | None = None  # 可选的会话ID，如果提供则关联到该会话


@router.post("/upload", response_model=ApiResponse)
async def upload_document(
        file: UploadFile = File(...),
        session_id: int | None = None,  # 可选的会话ID
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    上传文档
    限制：5MB以内，仅支持pdf/txt
    
    Query Parameters:
        session_id: 可选，如果提供则将文档关联到该会话
    """
    # 1. 验证文件类型
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return response.error_response({"message": "文件类型不支持"})

    # 2. 读取文件内容并验证大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return response.error_response({"message": "文件过大"})

    # 3. 如果提供了session_id，验证会话归属
    if session_id:
        from sqlalchemy import select
        from app.models.chat import ChatSession
        
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user["user_id"]
        )
        result = db.execute(stmt)
        session = result.scalars().first()
        
        if not session:
            return response.error_response({"message": "会话不存在或无访问权限"})

    # 4. 生成存储路径
    year_month = datetime.now().strftime("%Y/%m")
    storage_dir = Path(UPLOAD_BASE_PATH) / year_month
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # 使用时间戳 + 原始文件名（不含扩展名）+ 扩展名
    from pathlib import PurePath
    original_name_without_ext = PurePath(file.filename).stem  # 去除扩展名
    storage_filename = f"{int(datetime.now().timestamp())}_{original_name_without_ext}.{file_extension}"
    storage_path = storage_dir / storage_filename

    # 5. 保存文件
    with open(storage_path, "wb") as f:
        f.write(content)

    # 6. 创建数据库记录（使用相对路径，不带前导斜杠）
    relative_path = f"{UPLOAD_BASE_PATH}/{year_month}/{storage_filename}"
    doc_repo = DocumentRepository(db)
    document = doc_repo.create(
        user_id=current_user["user_id"],
        original_name=file.filename,
        storage_path=relative_path,
        file_size=len(content),
        file_extension=file_extension,
        mime_type=file.content_type
    )

    # 7. 如果提供了session_id，关联文档和会话
    if session_id:
        from app.models.chat import session_documents, ChatSession
        
        # 插入中间表记录
        insert_stmt = session_documents.insert().values(
            session_id=session_id,
            document_id=document.id
        )
        db.execute(insert_stmt)
        
        # 标记会话为 RAG 会话
        session.is_rag_session = True
        
        db.commit()

    return response.success_response(data={
        "document_id": document.id,
        "file_name": file.filename,
        "file_size": len(content),
        "session_id": session_id  # 返回关联的会话ID
    })


@router.post("/sessions/{session_id}/query", response_model=ApiResponse)
async def rag_query(
        session_id: int,
        request: RAGQueryRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    基于指定文档进行RAG问答
    
    Path Parameters:
        session_id: 会话ID
    
    Request Body:
    {
        "document_ids": [1, 2, 3],  // 要检索的文档ID列表
        "question": "用户的问题"     // 用户问题
    }
    """
    # 1. 验证会话归属
    from sqlalchemy import select
    from app.models.chat import ChatSession
    
    stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user["user_id"]
    )
    result = db.execute(stmt)
    session = result.scalars().first()

    if not session:
        return response.error_response({"message": "会话不存在或无访问权限"})

    # 2. 验证文档归属
    doc_repo = DocumentRepository(db)
    for doc_id in request.document_ids:
        doc = doc_repo.get_by_id(doc_id)
        if not doc or doc.user_id != current_user["user_id"]:
            return response.error_response({ "message": f"文档 {doc_id} 不存在或无访问权限"})

    # 3. 执行RAG查询
    rag_service = RAGService()
    result_data = await rag_service.query_rag(
        session_id=session_id,
        user_id=current_user["user_id"],
        document_ids=request.document_ids,
        question=request.question,
        db=db
    )

    # 4. 保存 RAG 对话记录
    import json
    from app.models.chat import RAGChatMessage
    
    # 构建来源信息
    source_info = [
        {
            "document_id": doc.metadata.get("document_id"),
            "filename": doc.metadata.get("original_filename"),
            "preview": doc.page_content[:200]
        }
        for doc in result_data.get("source_documents", [])
    ]
    
    rag_message = RAGChatMessage(
        session_id=session_id,
        user_question=request.question,
        ai_answer=result_data["answer"],
        document_ids=json.dumps(request.document_ids),
        source_info=json.dumps(source_info, ensure_ascii=False)
    )
    db.add(rag_message)
    db.commit()

    return response.success_response(data={
        "answer": result_data["answer"],
        "sources": [
            {
                "document_id": doc.metadata.get("document_id"),
                "filename": doc.metadata.get("original_filename"),
                "preview": doc.page_content[:200],
                "score": None  # ChromaDB 默认不返回分数
            }
            for doc in result_data.get("source_documents", [])
        ]
    })


@router.get("/sessions/{session_id}/documents", response_model=ApiResponse)
async def get_session_documents(
        session_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取会话关联的所有文档
    
    Path Parameters:
        session_id: 会话ID
    
    Returns:
        文档列表，包含文档ID、文件名、文件大小等信息
    """
    # 1. 验证会话归属
    from sqlalchemy import select
    from app.models.chat import ChatSession, session_documents
    
    stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user["user_id"]
    )
    result = db.execute(stmt)
    session = result.scalars().first()

    if not session:
        return response.error_response({"message": "会话不存在或无访问权限"})

    # 2. 查询会话关联的所有文档
    stmt = (
        select(session_documents.c.document_id)
        .where(session_documents.c.session_id == session_id)
    )
    result = db.execute(stmt)
    document_ids = [row[0] for row in result]

    # 3. 获取文档详细信息
    doc_repo = DocumentRepository(db)
    documents = []
    for doc_id in document_ids:
        doc = doc_repo.get_by_id(doc_id)
        if doc:
            documents.append({
                "id": doc.id,
                "original_name": doc.original_name,
                "file_size": doc.file_size,
                "file_extension": doc.file_extension,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
            })

    return response.success_response(data={
        "session_id": session_id,
        "document_count": len(documents),
        "documents": documents
    })


@router.get("/sessions/{session_id}/history", response_model=ApiResponse)
async def get_rag_history(
        session_id: int,
        page: int = 1,
        page_size: int = 20,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取会话的 RAG 对话历史
    
    Path Parameters:
        session_id: 会话ID
    
    Query Parameters:
        page: 页码（从1开始）
        page_size: 每页数量
    
    Returns:
        RAG 对话历史记录列表
    """
    import json
    from sqlalchemy import select
    from app.models.chat import ChatSession, RAGChatMessage
    
    # 1. 验证会话归属
    stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user["user_id"]
    )
    result = db.execute(stmt)
    session = result.scalars().first()

    if not session:
        return response.error_response({"message": "会话不存在或无访问权限"})

    # 2. 分页查询 RAG 对话记录
    offset = (page - 1) * page_size
    stmt = (
        select(RAGChatMessage)
        .where(RAGChatMessage.session_id == session_id)
        .order_by(RAGChatMessage.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = db.execute(stmt)
    rag_messages = result.scalars().all()

    # 3. 格式化返回数据
    history = []
    for msg in rag_messages:
        # 解析 JSON 字段
        try:
            document_ids = json.loads(msg.document_ids) if msg.document_ids else []
            source_info = json.loads(msg.source_info) if msg.source_info else []
        except json.JSONDecodeError:
            document_ids = []
            source_info = []
        
        history.append({
            "id": msg.id,
            "user_question": msg.user_question,
            "ai_answer": msg.ai_answer,
            "document_ids": document_ids,
            "source_info": source_info,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        })

    # 4. 获取总数
    from sqlalchemy import func
    count_stmt = (
        select(func.count(RAGChatMessage.id))
        .where(RAGChatMessage.session_id == session_id)
    )
    total = db.execute(count_stmt).scalar() or 0

    return response.success_response(data={
        "session_id": session_id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        "history": history
    })
