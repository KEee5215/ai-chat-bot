/// <reference types="vite/client" />

// uni-app 全局对象类型声明（用于兼容小程序环境）
declare const uni: {
  getStorageSync?: (key: string) => any;
  setStorageSync?: (key: string, value: any) => void;
  removeStorageSync?: (key: string) => void;
  showToast?: (options: { title: string; icon?: string; duration?: number }) => void;
  reLaunch?: (options: { url: string }) => void;
};
