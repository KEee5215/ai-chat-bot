<template>
  <fieldset
    class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4"
  >
    <legend class="fieldset-legend text-3xl text-[#1179a9]">Login</legend>

    <label class="label">Username</label>
    <input
      type="username"
      class="input"
      placeholder="username"
      v-model="username"
    />

    <label class="label">Password</label>
    <input
      type="password"
      class="input"
      placeholder="Password"
      v-model="password"
    />

    <button class="btn btn-neutral mt-4" @click="login">Login</button>
  </fieldset>
</template>

<script setup lang="ts">
import { userLogin } from "@/api/user/user";

import { ref } from "vue";

import { useRouter } from "vue-router";
const router = useRouter();

const username = ref("");
const password = ref("");

async function login() {
  try {
    // 验证输入
    if (!username.value || !password.value) {
      alert("请输入用户名和密码");
      return;
    }

    console.log("发送登录请求:", {
      username: username.value,
      password: password.value,
    });

    const response: any = await userLogin(username.value, password.value);
    console.log("登录响应:", response);
    console.log("登录成功，token:", response.access_token);

    // 保存 token 和用户信息（根据实际后端返回的数据结构调整）
    if (response.access_token) {
      console.log("Token:", response.access_token);
      localStorage.setItem("token", response.access_token);
      localStorage.setItem("username", response.username || username.value);
      localStorage.setItem("user_id", response.user_id);

      console.log("Token 已保存:", response.access_token);

      // 跳转到主页
      router.push("/chat");
      // alert("登录成功！");
    } else {
      alert("登录成功，但未获取到 Token");
    }
  } catch (error: any) {
    console.error("登录失败:", error);
    console.error("错误详情:", error.response?.data);
    console.error("状态码:", error.response?.status);
    console.error(
      "完整错误对象:",
      JSON.stringify(error.response?.data, null, 2),
    );

    // 显示具体错误信息
    const errorMsg =
      error.response?.data?.message ||
      error.response?.data?.msg ||
      "登录失败，请检查用户名和密码";
    alert(errorMsg);
  }
}
</script>

<style scoped></style>
