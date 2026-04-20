# app/repository/document_repo.py

from sqlalchemy.orm import Session
from app.models.chat import Document
from typing import Optional, List


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, original_name: str, storage_path: str,
               file_size: int, file_extension: str, mime_type: str = None) -> Document:
        """创建文档记录"""
        doc = Document(
            user_id=user_id,
            original_name=original_name,
            storage_path=storage_path,
            file_size=file_size,
            file_extension=file_extension,
            mime_type=mime_type
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        return self.db.query(Document).filter(Document.id == doc_id).first()

    # def get_by_hash_and_user(self, file_hash: str, user_id: int) -> Optional[Document]:
    #     """检查用户是否已上传相同文件（通过hash判断）"""
    #     # 注意：需要在Document表中添加file_hash字段
    #     return self.db.query(Document).filter(
    #         Document.file_hash == file_hash,
    #         Document.user_id == user_id
    #     ).first()

    def get_user_documents(self, user_id: int) -> List[Document]:
        """获取用户的所有文档"""
        return self.db.query(Document).filter(
            Document.user_id == user_id
        ).order_by(Document.uploaded_at.desc()).all()

    def delete(self, doc_id: int, user_id: int) -> bool:
        """删除文档（需验证归属）"""
        doc = self.db.query(Document).filter(
            Document.id == doc_id,
            Document.user_id == user_id
        ).first()

        if not doc:
            return False

        # 删除物理文件
        import os
        from pathlib import Path
        file_path = Path(doc.storage_path)
        if file_path.exists():
            file_path.unlink()

        # 删除数据库记录
        self.db.delete(doc)
        self.db.commit()
        return True
