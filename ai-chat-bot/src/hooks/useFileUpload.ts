/**
 * 文件上传函数
 * @param file - 要上传的文件
 */
async function uploadFile(file: File) {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("未授权：请重新登录");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/chat/upload", {
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
