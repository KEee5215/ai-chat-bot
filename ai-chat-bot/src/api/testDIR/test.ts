import service from "@/utils/reuqest";

export function getAllData() {
  return service({
    url: "/item/getAll",
    method: "get",
  });
}
