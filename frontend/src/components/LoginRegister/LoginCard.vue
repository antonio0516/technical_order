<script setup lang="ts">
import { ref } from "vue";
import { rules } from "@/library/inputRules";
import { config } from "@/config";
import axios from "axios";

// toast
// import { toast } from "vue3-toastify";
import { getCurrentInstance } from 'vue'

import "vue3-toastify/dist/index.css";

import { authStore } from "@store/authStore";

import { useRouter } from "vue-router";

let accountInput = ref("");
let passwordInput = ref("");

let form: any = ref(null);

const router = useRouter();

const clearInput = () => {
  accountInput.value = "";
  passwordInput.value = "";
};

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

const emits = defineEmits(["switchAuthView"]);

const login = async () => {
  if (!((await form.value.validate()).valid)) return;

  const data = {
    account: accountInput.value,
    password: passwordInput.value,
  };
  const res = await axios
    .post(`${config.BACKEND_URL}/auth/login`, data)
    .then((res) => {
      console.log(res);
      if (res.status === 200) {
        authStore().setToken(res.data.token);
        console.log(authStore().getToken);
        router.push("/function_panel/0");
        $toast?.success("登入成功", {});
      }
    })
    .catch((err) => {
      console.log(err);
      if (
        err.response.status === 400 ||
        err.response.status === 401 ||
        err.response.status === 404
      ) {
        $toast?.error(err.response.data.detail, {});
      } else if (err.response.status === 500) {
        $toast?.error("伺服器錯誤", {});
      } else {
        $toast?.error("未知錯誤", {});
      }
    });
};
</script>

<template>
  <v-container class="mx-0">
    <v-row class="" align="center" style="height: 100vh; width: 96vw">
      <v-card width="20vw" height="70vh" class="pa-5 ml-10">
        <div style="font-size: 1.5em">登入頁面</div>
        <v-form ref="form">
          <div class="mt-5">
            <v-text-field
              density="compact"
              label="教官帳號"
              type="input"
              :rules="[
                rules.required,
                rules.accountLength,
                rules.englishAndNumber,
              ]"
              variant="outlined"
              class="mb-2 input-remove-padding"
              v-model="accountInput"
            >
            </v-text-field>
            <v-text-field
              density="compact"
              label="密碼"
              type="password"
              variant="outlined"
              :rules="[
                rules.required,
                rules.passwordLength,
                rules.englishAndNumber,
              ]"
              class="mb-2 input-remove-padding"
              v-model="passwordInput"
            >
            </v-text-field>
          </div>
        </v-form>
        <div class="text-right mt-2">
          <v-btn width="100%" :rounded="true" color="primary" @click="login" style="font-size: 0.75em">
            登入
          </v-btn>
        </div>
        <!-- <div class="text-right mt-3">
          <v-btn
            variant="outlined"
            width="100%"
            :rounded="true"
            color="secondary"
            @click="$emit('switchAuthView', 'register')"
          >
            註冊
          </v-btn>
        </div>
        <div class="text-right mt-3">
          <v-btn
            variant="text"
            width="100%"
            :rounded="true"
            @click="$emit('switchAuthView', 'forget-password')"
          >
            忘記密碼
          </v-btn>
        </div> -->
      </v-card>
    </v-row>
  </v-container>
</template>

<style>
.input-remove-padding .v-field__input {
  padding-top: 0px;
  padding-bottom: 0px;
  font-size: 1.3em;
}
</style>
