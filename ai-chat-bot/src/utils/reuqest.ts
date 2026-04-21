import axios from "axios";

// ===== 1. 创建实例 =====
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json;charset=UTF-8",
  },
});

// ===== 2. 防重复请求（关键！）=====
const pending = new Map();
const getPendingKey = (config: any) =>
  [
    config.method,
    config.url,
    JSON.stringify(config.params),
    JSON.stringify(config.data),
  ].join("&");

const removePending = (config: any) => {
  const key = getPendingKey(config);
  if (pending.has(key)) {
    pending.get(key)?.abort?.(); // 取消上一次请求
    pending.delete(key);
  }
};

// 获取 uni 对象（兼容小程序环境）
const getUni = () => {
  return typeof window !== "undefined" ? (window as any).uni : undefined;
};

// ===== 3. 请求拦截器 =====
service.interceptors.request.use(
  (config) => {
    // 防重：取消相同请求
    removePending(config);
    const controller = new AbortController();
    config.signal = controller.signal;
    pending.set(getPendingKey(config), controller);

    // 自动加 token（兼容 localStorage / uni.getStorageSync）
    let token: string | null = null;
    if (typeof localStorage !== "undefined") {
      // Web 环境
      token = localStorage.getItem("token");
    } else {
      // 小程序环境
      const uni = getUni();
      if (uni && uni.getStorageSync) {
        token = uni.getStorageSync("token");
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ===== 4. 响应拦截器 =====
service.interceptors.response.use(
  (response) => {
    // 清除 pending
    removePending(response.config);

    const res = response.data;

    // 判断后端返回格式
    // 格式1: { code: 200, data: {...}, msg: "成功" }
    // 格式2: 直接返回业务数据 { user_id, username, token }
    if (res.code !== undefined) {
      // 有 code 字段的格式
      if (res.code === 200 || res.code === 0) {
        return res.data || res; // 返回 data 或整个响应
      }

      // 统一错误提示
      const uni = getUni();
      if (uni && uni.showToast) {
        uni.showToast({ title: res.msg || "操作失败", icon: "none" });
      } else if (typeof alert !== "undefined") {
        alert(res.msg || "请求失败");
      }
      return Promise.reject(res);
    } else {
      // 直接返回业务数据的格式（没有 code 字段）
      // 假设 HTTP 状态码 200 就代表成功
      return res;
    }
  },
  (error) => {
    removePending(error.config);

    // 如果是请求被取消的错误，直接返回，不显示提示
    if (error.name === "CanceledError" || error.code === "ERR_CANCELED") {
      return Promise.reject(error);
    }

    let msg = "网络异常，请稍后重试";
    if (error.message?.includes("timeout")) msg = "请求超时";
    if (error.code === "ECONNABORTED") msg = "请求已取消";
    if (error.response?.status === 401) {
      msg = "登录已过期";
      // 清 token + 跳登录
      if (typeof localStorage !== "undefined") {
        localStorage.removeItem("token");
      }
      const uni = getUni();
      if (uni && uni.removeStorageSync) {
        uni.removeStorageSync("token");
      }
      if (typeof location !== "undefined") {
        location.href = "/login"; // Web
      }
      if (uni && uni.reLaunch) {
        uni.reLaunch({ url: "/pages/login/login" }); // 小程序
      }
    }
    if (error.response?.status === 403) msg = "权限不足";
    if (error.response?.status === 500) msg = "服务器开小差了";

    const uni = getUni();
    if (uni && uni.showToast) {
      uni.showToast({ title: msg, icon: "none" });
    } else if (typeof alert !== "undefined") {
      alert(msg);
    }
    return Promise.reject(error);
  },
);

export default service;
