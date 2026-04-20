# app/services/rag_service.py
import logging
from typing import List, Optional
from langchain_chroma import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_llm
from app.models.chat import Document
from app.repository.chat_repo import ChatSessionRepository
from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.embedding_model = self._load_embedding_model()
        self.llm = get_llm()  # 复用你现有的LLM配置
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )

    def _load_embedding_model(self):
        """加载BGE embedding模型（单例）"""
        return HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def _get_collection_name(self, user_id: int, session_id: int) -> str:
        """生成Collection名称"""
        return f"user_{user_id}_session_{session_id}"

    def _get_or_create_vector_store(self, session_id: int, user_id: int,
                                    document_ids: List[int], db):
        """
        获取或创建向量存储
        如果Collection不存在，则从关联的Documents中解析并索引
        """
        from chromadb.config import Settings
        import chromadb

        chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

        collection_name = self._get_collection_name(user_id, session_id)
        logger.info(f"📦 Collection名称: {collection_name}")

        # 检查Collection是否已存在
        existing_collections = chroma_client.list_collections()
        collection_exists = any(c.name == collection_name for c in existing_collections)
        
        logger.info(f"🔍 Collection是否存在: {collection_exists}")

        if not collection_exists:
            logger.info(f"🆕 Collection不存在，开始索引文档...")
            logger.info(f"   文档IDs: {document_ids}")
            # 首次使用，需要索引所有关联的文档
            self._index_documents_for_session(
                document_ids, collection_name, chroma_client, db
            )
            logger.info(f"✅ 文档索引完成")
        else:
            logger.info(f"♻️ Collection已存在，跳过索引")

        # 返回向量存储
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            client=chroma_client
        )
        
        # 检查Collection中的文档数量
        collection = vector_store._collection
        doc_count = collection.count()
        logger.info(f"📊 Collection中文档数量: {doc_count}")

        return vector_store

    def _index_documents_for_session(self, document_ids: List[int],
                                     collection_name: str,
                                     chroma_client,
                                     db):
        """
        为会话索引所有关联的文档
        同步处理，适合小文件
        """
        from app.repository.document_repo import DocumentRepository

        logger.info(f"\n📑 开始索引 {len(document_ids)} 个文档")
        
        doc_repo = DocumentRepository(db)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            client=chroma_client
        )

        all_chunks = []

        for idx, doc_id in enumerate(document_ids, 1):
            logger.info(f"\n[{idx}/{len(document_ids)}] 处理文档 ID: {doc_id}")
            
            # 1. 获取文档信息
            doc = doc_repo.get_by_id(doc_id)
            if not doc:
                logger.warning(f"   ⚠️ 文档 ID {doc_id} 不存在，跳过")
                continue
            
            logger.info(f"   📄 文件名: {doc.original_name}")
            logger.info(f"   📂 路径: {doc.storage_path}")

            try:
                # 2. 根据文件类型选择loader
                chunks = self._load_and_split_document(doc)
                logger.info(f"   ✂️ 分割成 {len(chunks)} 个片段")
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"   ❌ 处理失败: {str(e)}")
                continue

        # 3. 批量存入ChromaDB
        logger.info(f"\n💾 准备存入 {len(all_chunks)} 个片段到 ChromaDB...")
        if all_chunks:
            # 添加元数据以便追溯
            for chunk in all_chunks:
                chunk.metadata["source_type"] = "rag_document"

            vector_store.add_documents(all_chunks)
            logger.info(f"✅ 成功存入 {len(all_chunks)} 个片段")
        else:
            logger.warning("⚠️ 没有片段需要存入")

    def _load_and_split_document(self, doc: Document) -> List:
        """
        加载并分割文档
        目前只支持PDF，后续可扩展docx、txt
        """
        from pathlib import Path

        # 处理存储路径（可能是相对路径或绝对路径）
        storage_path = doc.storage_path
        file_path = Path(storage_path)
        
        # 如果是相对路径，转换为绝对路径（相对于项目根目录）
        if not file_path.is_absolute():
            # 获取项目根目录（当前工作目录）
            project_root = Path.cwd()
            file_path = project_root / storage_path

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 根据文件扩展名选择loader
        extension = doc.file_extension.lower()

        if extension == "pdf":
            loader = PyMuPDFLoader(str(file_path))
            documents = loader.load()
        elif extension == "txt":
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents = loader.load()
        else:
            raise ValueError(f"不支持的文件类型: {extension}")

        # 分割文档
        chunks = self.text_splitter.split_documents(documents)

        # 为每个chunk添加文档ID元数据
        for chunk in chunks:
            chunk.metadata["document_id"] = doc.id
            chunk.metadata["original_filename"] = doc.original_name

        return chunks

    def create_rag_chain(self, session_id: int, user_id: int,
                         document_ids: List[int], db):
        """
        创建带记忆的RAG链
        使用 LangChain LCEL (LangChain Expression Language)
        """
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser

        # 1. 获取向量存储
        vector_store = self._get_or_create_vector_store(
            session_id, user_id, document_ids, db
        )

        # 2. 创建retriever（检索器）
        filter_criteria = {"document_id": {"$in": document_ids}}

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,
                "filter": filter_criteria  # ✅ 限制只检索指定的文档
            }
        )

        # 3. 自定义Prompt模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个严谨的文档问答助手。请**严格仅根据**下方的【参考资料】来回答用户的问题。

        【参考资料】：
        {context}

        【回答规则】：
        1. **必须**仅依据参考资料回答，**严禁**使用你训练数据中的外部知识。
        2. 如果参考资料中**没有**包含问题的答案，请直接回答：“根据当前文档，无法回答该问题。”，**不要**尝试编造。
        3. 回答时请注明引用了哪个文件（通过元数据中的文件名）。
        4. 保持回答简洁、专业。"""),
            ("human", "{question}")
        ])

        # 4. 定义上下文格式化函数
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # 5. 使用 LCEL 构建 RAG 链
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return rag_chain

    async def query_rag(self, session_id: int, user_id: int,
                        document_ids: List[int], question: str,
                        db):
        """
        RAG问答（非流式）
        使用 LCEL 构建的 RAG 链
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"开始 RAG 查询")
        logger.info(f"会话ID: {session_id}, 用户ID: {user_id}")
        logger.info(f"文档IDs: {document_ids}")
        logger.info(f"问题: {question}")
        logger.info(f"{'='*60}")
        
        # 1. 获取向量存储
        vector_store = self._get_or_create_vector_store(
            session_id, user_id, document_ids, db
        )
        
        # 2. 先测试检索，看看是否能找到相关内容
        filter_criteria = {"document_id": {"$in": document_ids}}
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,
                "filter": filter_criteria
            }
        )
        
        # 执行检索
        docs = retriever.invoke(question)
        logger.info(f"✅ 检索到 {len(docs)} 个相关文档片段")
        
        if len(docs) == 0:
            logger.warning("⚠️ 警告: 没有检索到任何内容！")
            return {
                "answer": "根据提供的文档，没有找到相关信息。",
                "source_documents": []
            }
        
        for i, doc in enumerate(docs):
            logger.info(f"\n📄 片段 {i+1}:")
            logger.info(f"   内容: {doc.page_content[:150]}...")
            logger.info(f"   来源: {doc.metadata.get('original_filename')}")
        
        # 3. 创建 RAG 链
        rag_chain = self.create_rag_chain(session_id, user_id, document_ids, db)
        
        # 4. 执行查询
        logger.info(f"\n🤖 正在生成答案...")
        answer = rag_chain.invoke(question)
        
        logger.info(f"\n✨ 生成的答案:")
        logger.info(f"{answer}")
        logger.info(f"{'='*60}\n")

        # 5. 返回答案和来源
        return {
            "answer": answer,
            "source_documents": docs  # 返回检索到的文档
        }
