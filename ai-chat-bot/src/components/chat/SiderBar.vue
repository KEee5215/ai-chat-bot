<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <!-- Navbar -->
      <nav class="navbar w-full bg-base-300">
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
            <button
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              data-tip="新增会话"
            >
              <!-- Home icon -->
              <PlusIcon></PlusIcon>
              <span class="is-drawer-close:hidden">新建会话</span>
            </button>
          </li>

          <!-- List item -->
          <li>
            <button
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              data-tip="某个会话"
            >
              <!-- Settings icon -->
              <BotIcon></BotIcon>
              <span class="is-drawer-close:hidden">对话一</span>
            </button>
          </li>

          <!-- List item -->
          <li>
            <button
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              data-tip="某个会话"
            >
              <!-- Settings icon -->
              <BotIcon></BotIcon>
              <span class="is-drawer-close:hidden">对话一</span>
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

            <!-- 设置按钮 -->
            <button
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right btn btn-ghost btn-circle btn-sm"
              data-tip="设置"
              @click="handleSettings"
            >
              <SettingsIcon></SettingsIcon>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import BotIcon from "../icons/BotIcon.vue";
import LogoIcon from "../icons/LogoIcon.vue";
import PlusIcon from "../icons/PlusIcon.vue";
import SettingsIcon from "../icons/SettingsIcon.vue";

// 模拟用户数据（实际项目中应该从 store 或 API 获取）
const username = computed(() => {
  // 这里可以从 localStorage 或其他状态管理中获取用户名
  return localStorage.getItem("username") || "用户";
});

// 获取用户名的首字母作为头像
const userInitial = computed(() => {
  const name = username.value;
  return name ? name.charAt(0).toUpperCase() : "U";
});

// 处理设置按钮点击
const handleSettings = () => {
  console.log("打开设置");
  // 这里可以跳转到设置页面或打开设置弹窗
  // router.push('/settings');
};
</script>

<style scoped></style>
