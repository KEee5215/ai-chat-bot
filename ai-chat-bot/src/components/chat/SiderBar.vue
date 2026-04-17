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
            <button
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right"
              data-tip="新增会话"
              @click="addSession"
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
            <label
              for="settingsBtn"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right btn btn-ghost btn-circle btn-sm"
              data-tip="设置"
              @click="handleSettings"
            >
              <SettingsIcon></SettingsIcon>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>

  <input type="checkbox" id="settingsBtn" class="modal-toggle" />
  <div class="modal" role="dialog">
    <div class="modal-box">
      <h3 class="text-lg font-bold">设置</h3>
      <p>退出登录</p>
      <button class="btn btn-circle btn-sm btn-success" @click="logout">
        <LogoutIcon></LogoutIcon>
      </button>
    </div>
    <label class="modal-backdrop" for="settingsBtn">Close</label>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
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

const $toast = useToast();

const userStore = useUserStore();

const username = computed(() => userStore.username);

// 处理设置按钮点击
const handleSettings = () => {
  console.log("打开设置");
  // 这里可以跳转到设置页面或打开设置弹窗
  // router.push('/settings');
};

const addSession = async () => {
  console.log("添加会话");
  // 这里可以跳转到添加会话页面或打开添加会话弹窗
  // router.push('/add-session');
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
