//存入本地存储的两个函数
export function setLocalStorage(key: string, value: Object) {
  localStorage.setItem(key, JSON.stringify(value));
}
