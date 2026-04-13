import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { setLocalStorage } from "@/utils/localstorage";

export const useUserStore = defineStore("user", () => {
  const userId = ref<string>("");
  const username = ref<string>("");

  function setUserId(useruserId: string) {
    userId.value = useruserId;
    setLoaclStorageUseruserId();
  }
  function clearUserId() {
    userId.value = "";
    setLocalStorage("userId", {});
  }

  function setLoaclStorageUseruserId() {
    setLocalStorage("userId", {
      userId: userId.value,
      userName: username.value,
    });
  }

  return { userId, setUserId, clearUserId };
});
