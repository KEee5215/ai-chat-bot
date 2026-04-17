<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <!-- Navbar -->
      <nav class="navbar w-full bg-base-300 fixed z-10">
        <label
          for="my-drawer-4"
          aria-label="open sidebar"
          class="btn btn-square btn-ghost"
        >
          <!-- Sidebar toggle icon -->
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
            class="my-1.5 inline-block size-4"
          >
            <path
              d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"
            ></path>
            <path d="M9 4v16"></path>
            <path d="M14 10l2 2l-2 2"></path>
          </svg>
        </label>
        <div class="px-4">AI-Chat-Bot</div>
      </nav>
      <!-- Page content here -->
      <div class="p-4">
        <RouterView></RouterView>
      </div>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label
        for="my-drawer-4"
        aria-label="close sidebar"
        class="drawer-overlay"
      ></label>
      <div
        class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-14 is-drawer-open:w-64"
      >
        <header class="w-full">
          <div class="flex items-center gap-2 p-4">
            <!-- Logo -->
            <LogoIcon class=""></LogoIcon>
            <!-- Title -->
            <a class="text-lg is-drawer-close:hidden"> KEee-Bot</a>
          </div>
        </header>
        <!-- Sidebar content here -->
        <ul class="menu w-full grow">
          <!-- List item -->
          <li>
            <label
              for="addSession"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              data-tip="新增会话"
              @click="showAddSessionModal"
            >
              <!-- Home icon -->
              <PlusIcon></PlusIcon>
              <span class="is-drawer-close:hidden">新建会话</span>
            </label>
          </li>

          <!-- List item -->
          <li v-for="session in sessionList" :key="session.id">
            <button
              :class="{ 'menu-active': sessionId === session.id }"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              :data-tip="session.title"
              @click="selectSession(session)"
            >
              <!-- Settings icon -->
              <BotIcon></BotIcon>
              <span class="is-drawer-close:hidden">{{ session.title }}</span>
            </button>
          </li>
        </ul>

        <!-- 底部用户信息区域 -->
        <div class="w-full border-t border-base-300 p-4">
          <div class="flex items-center justify-between gap-2">
            <!-- 用户头像和名称 -->
            <div class="flex items-center gap-2 overflow-hidden">
              <div class="avatar">
                <div class="w-8 rounded-full">
                  <img
                    src="https://img.daisyui.com/images/profile/demo/yellingcat@192.webp"
                  />
                </div>
              </div>
              <div class="is-drawer-close:hidden flex-1 overflow-hidden">
                <p class="truncate text-sm font-medium">{{ username }}</p>
              </div>
            </div>

            <!-- 退出登录按钮 -->
            <label
              class="btn-success is-drawer-close:tooltip is-drawer-close:tooltip-right btn btn-circle btn-sm"
              data-tip="设置"
              @click="logout"
            >
              <LogoutIcon></LogoutIcon>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- 新建会话弹窗 -->
  <dialog id="addSessionBtn" class="modal">
    <div class="modal-box w-full max-w-md shadow-2xl">
      <!-- 关闭按钮 -->
      <form method="dialog">
        <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
          ✕
        </button>
      </form>

      <!-- 标题和描述 -->
      <div class="mb-6">
        <h3 class="text-2xl font-bold text-base-content">新建会话</h3>
        <!-- <p class="text-sm text-base-content/70 mt-1">
          为会话取一个有意义的名称
        </p> -->
      </div>

      <!-- 输入框 -->
      <div class="form-control w-full">
        <label class="label pb-2">
          <!-- <span class="label-text font-medium">会话标题</span> -->
        </label>
        <input
          v-model="sessionTitle"
          type="text"
          placeholder="请输入会话标题..."
          class="input input-bordered input-sm w-full focus:outline-none focus:input-primary"
          @keyup.enter="confirmAddSession"
        />
      </div>

      <!-- 提示文字 -->
      <p class="text-xs text-base-content/50 mt-2">最多可输入 50 个字符</p>

      <!-- 按钮区域 -->
      <div class="modal-action mt-6 gap-2">
        <form method="dialog" class="flex gap-2 w-full">
          <button class="btn btn-ghost flex-1">取消</button>
          <button
            type="button"
            @click="confirmAddSession"
            class="btn btn-primary flex-1"
          >
            创建
          </button>
        </form>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import BotIcon from "../icons/BotIcon.vue";
import LogoIcon from "../icons/LogoIcon.vue";
import PlusIcon from "../icons/PlusIcon.vue";
import SettingsIcon from "../icons/SettingsIcon.vue";
import { useRouter } from "vue-router";
const router = useRouter();
import { useUserStore } from "@/stores/user";

import LogoutIcon from "../icons/LogoutIcon.vue";

import { useToast } from "vue-toast-notification";
import "vue-toast-notification/dist/theme-sugar.css";
import { addSession, getSession } from "@/api/chat/chat";
import { useMessageStore } from "@/stores/message";

const $toast = useToast();

const userStore = useUserStore();
const messageStore = useMessageStore();

const username = computed(() => userStore.username);

const sessionTitle = ref("");

const sessionId = ref(messageStore.sessionId);

interface Session {
  id: string;
  title: string;
  createTime: string;
}

const sessionList = ref<Session[]>([]);

// 选中会话
const selectSession = (session: Session) => {
  sessionId.value = session.id;
  messageStore.setSessionId(session.id);
  // 可选：跳转到对应会话页面
  router.push(`/chat/${session.id}`);
};

// 显示新建会话弹窗
const showAddSessionModal = () => {
  const dialog = document.getElementById("addSessionBtn") as HTMLDialogElement;
  dialog?.showModal();
};

// 关闭新建会话弹窗
const closeAddSessionModal = () => {
  const dialog = document.getElementById("addSessionBtn") as HTMLDialogElement;
  dialog?.close();
};

// 获取会话列表
const loadSessionList = async () => {
  try {
    const res: any = await getSession(1, 10);
    sessionList.value = res;
  } catch (error) {
    console.error("加载会话列表失败:", error);
  }
};

// 初始化时加载
onMounted(() => {
  loadSessionList();
});
// 新增会话
const confirmAddSession = async () => {
  try {
    if (!sessionTitle.value.trim()) {
      $toast.open({
        message: "请输入会话标题",
        type: "warning",
        position: "top-right",
      });
      return;
    }

    await addSession(sessionTitle.value);

    $toast.open({
      message: "添加成功",
      type: "success",
      position: "top-right",
    });

    // 重新加载会话列表
    await loadSessionList();

    // 清空输入框并关闭弹窗
    sessionTitle.value = "";
    closeAddSessionModal();
  } catch (error) {
    $toast.open({
      message: "添加失败，请重试",
      type: "error",
      position: "top-right",
    });
    console.error(error);
  }
};

const logout = async () => {
  // 这里可以跳转到登录页面或打开登录弹窗
  router.push("/login");
  $toast.open({
    message: "退出登录",
    type: "success",
    position: "top-right",
  });
  userStore.logout();
};
</script>

<style scoped></style>
