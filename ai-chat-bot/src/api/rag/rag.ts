import service from "@/utils/reuqest";

// 基于指定文档进行 RAG 问答
export const ragChat = (
  session_id: string,
  document_ids: number[],
  question: string,
) => {
  return service.post(`/rag/sessions/${session_id}/query`, {
    document_ids,
    question,
  });
};

// 获取会话关联的所有文档
export const getSessionDocuments = (session_id: string) => {
  return service.get(`/rag/sessions/${session_id}/documents`);
};

//获取会话历史消息,分页
export const getSessionMessages = (
  session_id: string,
  page: number,
  page_size: number,
) => {
  return service.get(`/rag/sessions/${session_id}/history`, {
    params: {
      page,
      page_size,
    },
  });
};
