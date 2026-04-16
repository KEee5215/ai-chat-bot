import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useMessageStore = defineStore("message", () => {
  interface Message {
    role: string;
    content: string;
  }

  const message = ref<Message[]>([
    { role: "user", content: "hello" },
    {
      role: "assistant",
      content:
        "# hello, \n ## aisd *ioha* sdoaisdhasidh<br>nsdnaiosdioasdadaiosdn",
    },
    { role: "user", content: "hello" },
    { role: "assistant", content: "hello" },
    { role: "user", content: "hello" },
    { role: "assistant", content: "helloasasfasfasfasf\n牛啊猴儿好大苏打" },
    { role: "user", content: "hello" },
    {
      role: "assistant",
      content:
        "# hello, \n ## aisd *ioha* sdoaisdhasidh<br>nsdnaiosdioasdadaiosdn",
    },
    { role: "user", content: "hello" },
    { role: "assistant", content: "hello" },
  ]);

  function addUserMessage(content: string) {
    message.value.push({ role: "user", content });
  }

  function removeUserMessage(index: number) {
    message.value.splice(index, 1);
  }

  function addAIMessage(content: string) {
    message.value.push({ role: "assistant", content });
  }

  function removeAIMessage(index: number) {
    message.value.splice(index, 1);
  }

  return {
    message,
    addUserMessage,
    removeUserMessage,
    addAIMessage,
    removeAIMessage,
  };
});
