# app/services/rag_service.py

from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_llm
from app.models.chat import Document
from app.repository.chat_repo import ChatSessionRepository
from sqlalchemy.ext.asyncio import AsyncSession


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
                                    document_ids: List[int], db: AsyncSession):
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

        # 检查Collection是否已存在
        existing_collections = chroma_client.list_collections()
        collection_exists = any(c.name == collection_name for c in existing_collections)

        if not collection_exists:
            # 首次使用，需要索引所有关联的文档
            self._index_documents_for_session(
                document_ids, collection_name, chroma_client, db
            )

        # 返回向量存储
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            client=chroma_client
        )

        return vector_store

    def _index_documents_for_session(self, document_ids: List[int],
                                     collection_name: str,
                                     chroma_client,
                                     db: AsyncSession):
        """
        为会话索引所有关联的文档
        同步处理，适合小文件
        """
        from app.repository.document_repo import DocumentRepository

        doc_repo = DocumentRepository(db)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            client=chroma_client
        )

        all_chunks = []

        for doc_id in document_ids:
            # 1. 获取文档信息
            doc = doc_repo.get_by_id(doc_id)
            if not doc:
                continue

            # 2. 根据文件类型选择loader
            chunks = self._load_and_split_document(doc)
            all_chunks.extend(chunks)

        # 3. 批量存入ChromaDB
        if all_chunks:
            # 添加元数据以便追溯
            for chunk in all_chunks:
                chunk.metadata["source_type"] = "rag_document"

            vector_store.add_documents(all_chunks)

    def _load_and_split_document(self, doc: Document) -> List:
        """
        加载并分割文档
        目前只支持PDF，后续可扩展docx、txt
        """
        from pathlib import Path

        file_path = Path(doc.storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {doc.storage_path}")

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
                         document_ids: List[int], db: AsyncSession):
        """
        创建带记忆的RAG链
        使用ConversationBufferWindowMemory实现滑动窗口
        """
        from langchain.chains import ConversationalRetrievalChain

        # 1. 获取向量存储
        vector_store = self._get_or_create_vector_store(
            session_id, user_id, document_ids, db
        )

        # 2. 创建retriever（检索器）
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # 返回最相关的5个片段
        )

        # 3. 创建对话记忆（滑动窗口，保留最近5轮）
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,  # 保留最近5轮对话
            return_messages=True,
            output_key="answer"
        )

        # 4. 自定义Prompt模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能文档问答助手。请基于以下参考资料和对话历史回答问题。

参考资料：
{context}

要求：
1. 优先根据参考资料回答，不要编造信息
2. 如果资料中没有相关信息，请明确说明
3. 引用资料时标注来源文件名
4. 结合对话历史保持回答的连贯性
5. 使用中文回答，简洁清晰"""),
            ("human", "{question}")
        ])

        # 5. 创建RAG链 - 注意: LangChain 1.x 推荐使用新的 API
        # ConversationalRetrievalChain 已被标记为过时
        # 这里暂时保留,但建议后续迁移到 create_retrieval_chain
        from langchain.chains import ConversationalRetrievalChain
        rag_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,  # 返回来源文档
            verbose=False
        )

        return rag_chain

    async def query_rag_stream(self, session_id: int, user_id: int,
                               document_ids: List[int], question: str,
                               db: AsyncSession):
        """
        RAG问答（流式返回）
        注意：ConversationalRetrievalChain默认不支持流式，需要特殊处理
        """
        # 方案A：使用非流式（简单）
        rag_chain = self.create_rag_chain(session_id, user_id, document_ids, db)
        result = rag_chain({"question": question})

        # 返回完整答案和来源
        return {
            "answer": result["answer"],
            "source_documents": result.get("source_documents", [])
        }

        # 方案B：如果需要流式，需要手动实现（较复杂）
        # 见下方说明
