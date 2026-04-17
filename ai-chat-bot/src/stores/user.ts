import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { setLocalStorage } from "@/utils/localstorage";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>("");
  const username = ref<string>("");

  function setToken(jwt: string) {
    token.value = jwt;
    setLocalStorage("token", jwt);
  }
  function clearToken() {
    token.value = "";
    localStorage.removeItem("token");
  }

  function setUsername(name: string) {
    username.value = name;
  }

  function clearUsername() {
    username.value = "";
  }

  function logout() {
    clearToken();
    clearUsername();
  }

  return { token, username, setToken, clearToken, setUsername, clearUsername, logout };
});
