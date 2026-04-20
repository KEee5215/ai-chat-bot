"""
测试 RAG 检索功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models import SyncSessionMaker
from app.services.rag_service import RAGService
from app.repository.document_repo import DocumentRepository

def test_rag_retrieval():
    """测试RAG检索"""
    db = SyncSessionMaker()
    
    try:
        # 1. 获取所有文档
        doc_repo = DocumentRepository(db)
        docs = doc_repo.get_user_documents(user_id=7)  # 替换为你的用户ID
        
        print(f"找到 {len(docs)} 个文档:")
        for doc in docs:
            print(f"  - ID: {doc.id}, 名称: {doc.original_name}, 路径: {doc.storage_path}")
        
        if not docs:
            print("没有文档，请先上传文件")
            return
        
        # 2. 测试加载和分割
        rag_service = RAGService()
        test_doc = docs[0]
        
        print(f"\n测试加载文档: {test_doc.original_name}")
        chunks = rag_service._load_and_split_document(test_doc)
        print(f"分割成 {len(chunks)} 个片段")
        
        if chunks:
            print(f"\n第一个片段内容:")
            print(chunks[0].page_content[:300])
            print(f"\n元数据: {chunks[0].metadata}")
        
        # 3. 测试向量检索
        print("\n" + "="*50)
        print("测试向量检索")
        print("="*50)
        
        question = "柯亿的女朋友是谁"
        print(f"\n问题: {question}")
        
        # 创建一个测试会话
        from app.models.chat import ChatSession
        from datetime import datetime
        
        # 查找或创建测试会话
        session = db.query(ChatSession).filter(
            ChatSession.user_id == test_doc.user_id
        ).first()
        
        if not session:
            session = ChatSession(
                user_id=test_doc.user_id,
                title="测试会话",
                is_deleted=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        print(f"使用会话 ID: {session.id}")
        
        # 获取向量存储（会触发索引）
        vector_store = rag_service._get_or_create_vector_store(
            session_id=session.id,
            user_id=test_doc.user_id,
            document_ids=[test_doc.id],
            db=db
        )
        
        # 执行检索
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.invoke(question)
        
        print(f"\n检索到 {len(retrieved_docs)} 个相关片段:")
        for i, doc in enumerate(retrieved_docs):
            print(f"\n片段 {i+1}:")
            print(f"  内容: {doc.page_content[:200]}...")
            print(f"  元数据: {doc.metadata}")
        
        if len(retrieved_docs) == 0:
            print("\n⚠️ 警告: 没有检索到任何内容！")
            print("可能原因:")
            print("  1. 文档没有被正确索引")
            print("  2. Embedding 质量问题")
            print("  3. 问题与文档内容不相关")
            
            # 检查 Collection 中的文档数量
            collection = vector_store._collection
            count = collection.count()
            print(f"\nCollection 中文档总数: {count}")
            
            if count > 0:
                # 获取所有文档看看
                all_docs = collection.get()
                print(f"存储的文档 IDs: {all_docs['ids'][:5]}...")  # 只显示前5个
                
    finally:
        db.close()

if __name__ == "__main__":
    test_rag_retrieval()
