import service from "@/utils/reuqest";

export const getUser = (id: string) => {
  return service.get(`/user/${id}`);
};

export function userLogin(username: string, password: string) {
  return service.post("/auth/login", { username, password });
}
//只删除token
// export function userLogout() {
//   return service.post("/auth/logout");
// }
