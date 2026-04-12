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
      <div class="p-4">Page Content</div>
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
        <header>
          <div class="flex items-center gap-2 p-4">
            <!-- Logo -->
            <LogoIcon></LogoIcon>
            <!-- Title -->
            <span class="is-drawer-close:hidden">KEee-Bot</span>
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
              <span class="is-drawer-close:hidden">Homepage</span>
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
              <span class="is-drawer-close:hidden">Settings</span>
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BotIcon from "../icons/BotIcon.vue";
import LogoIcon from "../icons/LogoIcon.vue";
import PlusIcon from "../icons/PlusIcon.vue";
</script>

<style scoped></style>
