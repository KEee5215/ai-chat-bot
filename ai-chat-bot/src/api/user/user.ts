import service from "@/utils/reuqest";

export const getUser = (id: string) => {
  return service.get(`/user/${id}`);
};

export function userLogin(username: string, password: string) {
  return service.post("/login", { username, password });
}
