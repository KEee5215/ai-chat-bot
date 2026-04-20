# app/api/v1/rag.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.auth import get_current_user_id, get_current_user
from app.dependencies import  get_db
from app.utils import response
from app.schemas.response import ApiResponse
from app.services.rag_service import RAGService
from app.repository.document_repo import DocumentRepository
import os
import hashlib
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/rag", tags=["RAG"])

# 文件上传配置
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"pdf", "txt"}  # 目前支持的类型
UPLOAD_BASE_PATH = "./uploads"


@router.post("/upload", response_model=ApiResponse)
async def upload_document(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    上传文档
    限制：5MB以内，仅支持pdf/txt
    """
    # 1. 验证文件类型
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return response.error_response({"message": "文件类型不支持"})

    # 2. 读取文件内容并验证大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return response.error_response({"message": "文件过大"})

    # 3. 计算文件hash（用于去重）
    # file_hash = hashlib.md5(content).hexdigest()

    # 4. 检查是否已上传过相同文件
    doc_repo = DocumentRepository(db)
    # existing_doc = doc_repo.get_by_hash_and_user(file_hash, current_user.id)
    # if existing_doc:
    #     return response.success_response(data={
    #         "document_id": existing_doc.id,
    #         "message": "文件已存在，直接使用"
    #     })

    # 5. 生成存储路径
    year_month = datetime.now().strftime("%Y/%m")
    storage_dir = Path(UPLOAD_BASE_PATH) / year_month
    storage_dir.mkdir(parents=True, exist_ok=True)
    # 时间戳命名
    storage_filename = f"{datetime.now().timestamp()}.{file_extension}"
    storage_path = storage_dir / storage_filename

    # 6. 保存文件
    with open(storage_path, "wb") as f:
        f.write(content)

    # 7. 创建数据库记录
    relative_path = f"/{UPLOAD_BASE_PATH}/{year_month}/{storage_filename}"
    document = doc_repo.create(
        user_id=current_user.id,
        original_name=file.filename,
        storage_path=relative_path,
        file_size=len(content),
        file_extension=file_extension,
        mime_type=file.content_type
    )

    return response.success_response(data={
        "document_id": document.id,
        "file_name": file.filename,
        "file_size": len(content)
    })


@router.post("/sessions/{session_id}/query", response_model=ApiResponse)
async def rag_query(
        session_id: int,
        document_ids: List[int],  # 前端传入要检索的文档ID列表
        question: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    基于指定文档进行RAG问答
    需要传入session_id和document_ids
    """
    # 1. 验证会话归属
    from app.repository.chat_repo import ChatSessionRepository
    session_repo = ChatSessionRepository(db)
    session = session_repo.get_by_id(session_id)

    if not session or session.user_id != current_user.id:
        return response.error_response({ "message": "会话不存在或无访问权限"})

    # 2. 验证文档归属
    doc_repo = DocumentRepository(db)
    for doc_id in document_ids:
        doc = doc_repo.get_by_id(doc_id)
        if not doc or doc.user_id != current_user.id:
            return response.error_response({ "message": "文档不存在或无访问权限"})

    # 3. 执行RAG查询
    rag_service = RAGService()
    result = await rag_service.query_rag_stream(
        session_id=session_id,
        user_id=current_user.id,
        document_ids=document_ids,
        question=question,
        db=db
    )

    # 4. 保存聊天记录（可选）
    # ... 保存到你现有的Chat表

    return response.success_response(data={
        "answer": result["answer"],
        "sources": [
            {
                "document_id": doc.metadata.get("document_id"),
                "filename": doc.metadata.get("original_filename"),
                "preview": doc.page_content[:200]
            }
            for doc in result.get("source_documents", [])
        ]
    })
