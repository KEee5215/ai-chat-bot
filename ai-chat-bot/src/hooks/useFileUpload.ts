/**
 * 文件上传函数
 * @param file - 要上传的文件
 * @param sessionId - 会话ID，将文档关联到该会话
 */
async function uploadFile(file: File, sessionId: string) {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("未授权：请重新登录");
  }

  // 文件大小限制：5MB
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    throw new Error("文件大小不能超过5MB");
  }

  // 文件类型限制：仅支持pdf和txt
  const allowedTypes = ["application/pdf", "text/plain"];
  const allowedExtensions = [".pdf", ".txt"];
  const fileExtension = "." + file.name.split(".").pop()?.toLowerCase();

  if (
    !allowedTypes.includes(file.type) &&
    !allowedExtensions.includes(fileExtension)
  ) {
    throw new Error("仅支持PDF和TXT格式的文件");
  }

  const formData = new FormData();
  formData.append("file", file);

  // 添加session_id作为查询参数
  const response = await fetch(`/api/rag/upload?session_id=${sessionId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("授权过期，请重新登录");
    }
    throw new Error(`文件上传失败: ${response.status}`);
  }

  const data = await response.json();
  console.log("文件上传成功:", data);
  return data;
}

export default uploadFile;
