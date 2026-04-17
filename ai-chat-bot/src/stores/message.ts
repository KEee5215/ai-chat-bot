import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useMessageStore = defineStore("message", () => {
  //   用户选择的会话ID
  const sessionId = ref<string>("");

  //   修改sessionId的函数
  function setSessionId(id: string) {
    sessionId.value = id;
  }

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

  // 更新AI消息内容
  function updateAIMessageContent(index: number, content: string) {
    if (message.value[index]) {
      message.value[index].content = content;
    }
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
    updateAIMessageContent,
    sessionId,
    setSessionId,
  };
});
