<template>
  <div
    class="flex flex-col h-screen w-full bg-gradient-to-b from-base-100 to-base-200"
  >
    <!-- 欢迎区域 -->
    <div class="flex-1 flex flex-col items-center justify-center px-4">
      <!-- Logo 和标题 -->
      <div class="text-center mb-12">
        <h1 class="text-8xl font-bold mb-2">KEEE Chat</h1>
        <p class="text-base-content/60">
          请选择开启一个新对话还是继续之前的对话
        </p>
      </div>

      <!-- 新建会话按钮 -->
      <button
        @click="startNewSession"
        class="btn btn-success btn-lg mb-12 px-8"
      >
        <span class="text-lg"> 创建一个新对话</span>
      </button>

      <!-- 历史会话列表 -->
      <div v-if="sessionList.length > 0" class="w-full max-w-2xl">
        <h2 class="text-lg font-semibold mb-4 text-center">最近的会话</h2>
        <div class="grid gap-3">
          <button
            v-for="session in sessionList"
            :key="session.id"
            @click="openSession(session.id)"
            class="btn btn-outline btn-block justify-start text-left"
          >
            <div class="flex-1 truncate">
              <p class="font-medium">{{ session.title }}</p>
              <p class="text-xs text-base-content/50">
                {{ formatDate(session.createTime) }}
              </p>
            </div>
            <span class="text-base-content/30"></span>
          </button>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div v-else class="text-center text-base-content/50">
        <p class="mb-4">尚未有任何会话历史</p>
        <p class="text-sm">点击上方按钮,开启一个新会话</p>
      </div>
    </div>

    <!-- 新建会话弹窗 -->
    <dialog id="newSessionModal" class="modal">
      <div class="modal-box w-full max-w-md">
        <form method="dialog">
          <button
            class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
          >
            ✕
          </button>
        </form>

        <div class="mb-6">
          <h3 class="text-2xl font-bold">新建会话</h3>
          <p class="text-sm text-base-content/60 mt-1">给本次会话起个名字</p>
        </div>

        <div class="form-control w-full">
          <input
            v-model="newSessionTitle"
            type="text"
            placeholder="请输入会话标题..."
            class="input input-bordered w-full focus:outline-none focus:input-primary"
            @keyup.enter="confirmNewSession"
          />
        </div>

        <div class="modal-action mt-6 gap-2">
          <form method="dialog" class="flex gap-2 w-full">
            <button class="btn btn-ghost flex-1">取消</button>
            <button
              type="button"
              @click="confirmNewSession"
              class="btn btn-primary flex-1"
            >
              创建
            </button>
          </form>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>关闭</button>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toast-notification";
import { getSession, addSession } from "@/api/chat/chat";
import PlusIcon from "../icons/PlusIcon.vue";

const router = useRouter();
const $toast = useToast();

interface Session {
  id: string;
  title: string;
  createTime: string;
}

const sessionList = ref<Session[]>([]);
const newSessionTitle = ref("");

// 加载历史会话
const loadSessions = async () => {
  try {
    const res: any = await getSession(1, 10);
    if (res && Array.isArray(res)) {
      sessionList.value = res;
    }
  } catch (error) {
    console.error("加载会话失败:", error);
  }
};

// 开启新会话
const startNewSession = () => {
  newSessionTitle.value = "";
  const dialog = document.getElementById(
    "newSessionModal",
  ) as HTMLDialogElement;
  dialog?.showModal();
};

// 确认创建新会话
const confirmNewSession = async () => {
  if (!newSessionTitle.value.trim()) {
    $toast.open({
      message: "Please enter a conversation title",
      type: "warning",
      position: "top-right",
    });
    return;
  }

  try {
    const res: any = await addSession(newSessionTitle.value);

    $toast.open({
      message: "Conversation created successfully",
      type: "success",
      position: "top-right",
    });

    // 跳转到新会话
    const sessionId = res?.id || res;
    await router.push(`/chat/${sessionId}`);
  } catch (error) {
    $toast.open({
      message: "Failed to create conversation",
      type: "error",
      position: "top-right",
    });
    console.error(error);
  }
};

// 进入历史会话
const openSession = (sessionId: string) => {
  router.push(`/chat/${sessionId}`);
};

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffTime = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;

  return date.toLocaleDateString();
};

// 页面挂载时加载会话列表
onMounted(() => {
  loadSessions();
});
</script>

<style scoped></style>
