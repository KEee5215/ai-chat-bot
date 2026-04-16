import service from "@/utils/reuqest";

// 创建新的会话
export const addSession = (title: string) => {
  return service.get(`/chat/session`);
};

// 分页获取会话列表
export const getSession = (page: number, pageSize: number) => {
  return service.get(`/chat/session/page=${page}&page_size=${pageSize}`);
};

// 获取会话内的消息列表
export const getMessage = (sessionId: string, limit: number) => {
  return service.get(`/chat/session/${sessionId}/message?limit=${limit}`);
};
