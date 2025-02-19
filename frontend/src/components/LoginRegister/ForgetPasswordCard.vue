<script setup lang="ts">
import { ref } from "vue";
import { rules } from "@/library/inputRules";

import axios from "axios";
import { config } from "@/config";
// toast
import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

import { authStore } from "@store/authStore";

let form1: any = ref(null);
let form2: any = ref(null);
let form3: any = ref(null);

const emits = defineEmits(["switchAuthView"]);

let step = ref(1);
let accountInput = ref("");
let userQuestion = ref("");
let answerInput = ref("");
let newPasswordInput = ref("");
let checkPasswordInput = ref("");

const setStep = (target: number) => {
  step.value = target;
};

const clearInput = () => {
  step.value = 1;
  accountInput.value = "";
  userQuestion.value = "";
  answerInput.value = "";
  newPasswordInput.value = "";
  checkPasswordInput.value = "";
};

const getUserSafeQuestion = async () => {
  const { valid } = await form1.value.validate();
  if (!valid) return;

  const res = await axios
    .get(`${config.BACKEND_URL}/users/${accountInput.value}/safe_question`, {})
    .then((res) => {
      if (res.status === 200) {
        userQuestion.value = res.data.safe_question;
        console.log(res.data.safe_question);
        setStep(2);
      }
    })
    .catch((err) => {
      if (err.response.status === 400 || err.response.status === 404) {
        toast.error(err.response.data.detail, {});
      } else if (err.response.status === 500) {
        toast.error("伺服器錯誤", {});
      } else {
        toast.error("未知錯誤", {});
      }
    });
};

const submitSafeAnswer = async () => {
  const { valid } = await form2.value.validate();
  if (!valid) return;

  const data = {
    account: accountInput.value,
    safe_answer: answerInput.value,
  };

  const res = await axios
    .post(`${config.BACKEND_URL}/auth/forget_password`, data)
    .then((res) => {
      if (res.status === 200) {
        authStore().setToken(res.data.token);
        setStep(3);
      }
    })
    .catch((err) => {
      console.log(err);
      if (
        err.response.status === 400 ||
        err.response.status === 401 ||
        err.response.status === 404
      ) {
        toast.error(err.response.data.detail, {});
      } else if (err.response.status === 500) {
        toast.error("伺服器錯誤", {});
      } else {
        toast.error("未知錯誤", {});
      }
    });
};

const submitNewPassword = async () => {
  const { valid } = await form3.value.validate();
  if (!valid) return;

  const data = {
    new_password: newPasswordInput.value,
    token: authStore().getToken,
  };

  const res = await axios
    .patch(`${config.BACKEND_URL}/users/${accountInput.value}/password`, data, {
    })
    .then((res) => {
      if (res.status === 200) {
        authStore().setToken("");
        clearInput();
        emits("switchAuthView", "login");
        toast.success("密碼修改成功", {});
      }
    })
    .catch((err) => {
      console.log(err);
      if (err.response.status === 400 || err.response.status === 404) {
        toast.error(err.response.data.detail, {});
      } else if (err.response.status === 401) {
        emits("switchAuthView", "forget-password");
        toast.error("身分驗證錯誤，請重新回答安全問題", {});
      } else if (err.response.status === 500) {
        toast.error("伺服器錯誤", {});
      } else {
        toast.error("未知錯誤", {});
      }
    });
};
</script>

<template>
  <v-container class="ml-0">
    <v-row class="" align="center" style="height: 97vh">
      <v-card width="30vw" height="70vh" class="pa-5 ml-10">
        <div style="font-size: 1.5em" class="mb-5">忘記密碼</div>
        <v-form ref="form1" v-if="step == 1">
          <div class="">
            <div class="mb-4">請輸入您的帳號：</div>
            <v-text-field
              :rules="[
                rules.required,
                rules.accountLength,
                rules.englishAndNumber,
              ]"
              density="compact"
              label="帳號（學號）"
              type="input"
              variant="outlined"
              class="mt-2"
              v-model="accountInput"
            >
            </v-text-field>
          </div>
        </v-form>
        <v-form ref="form2" v-if="step == 2">
          <div>
            <div class="mb-4">
              <span>您設置的安全性問題：「 </span>
              <span class="font-weight-bold">{{ userQuestion }}</span>
              <span> 」</span>
            </div>
            <v-text-field
              density="compact"
              label="您的回答"
              :rules="[rules.required, rules.safeAnswerLength]"
              type="input"
              variant="outlined"
              v-model="answerInput"
            >
            </v-text-field>
          </div>
        </v-form>
        <v-form v-if="step == 3" ref="form3">
          <div>
            <div class="mb-4">請輸入您的新密碼：</div>
            <v-text-field
              density="compact"
              label="密碼"
              type="password"
              :rules="[
                rules.required,
                rules.passwordLength,
                rules.englishAndNumber,
              ]"
              variant="outlined"
              v-model="newPasswordInput"
            >
            </v-text-field>
            <v-text-field
              density="compact"
              label="再次輸入密碼"
              type="password"
              variant="outlined"
              :rules="[
                rules.required,
                rules.passwordLength,
                rules.englishAndNumber,
                rules.checkPassword(newPasswordInput, checkPasswordInput),
              ]"
              v-model="checkPasswordInput"
            >
            </v-text-field>
          </div>
        </v-form>
        <div class="text-right mt-3">
          <div v-if="step == 1">
            <v-btn
              width="100%"
              :rounded="true"
              color="primary"
              @click="getUserSafeQuestion"
            >
              下一步
            </v-btn>
          </div>
          <div v-if="step == 2">
            <v-spacer></v-spacer>
            <v-container>
              <v-row justify="space-between">
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="secondary"
                  @click="setStep(1)"
                >
                  上一步
                </v-btn>
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="primary"
                  @click="submitSafeAnswer"
                >
                  提交
                </v-btn>
              </v-row>
            </v-container>
          </div>
          <div v-if="step == 3">
            <v-spacer></v-spacer>
            <v-container>
              <v-row justify="space-between">
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="secondary"
                  @click="setStep(2)"
                >
                  上一步
                </v-btn>
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="primary"
                  @click="submitNewPassword"
                >
                  提交
                </v-btn>
              </v-row>
            </v-container>
          </div>
          <v-btn
            class="mt-4"
            variant="outlined"
            width="100%"
            :rounded="true"
            color="secondary"
            @click="$emit('switchAuthView', 'register')"
          >
            註冊
          </v-btn>
        </div>
      </v-card>
    </v-row>
  </v-container>
</template>

<style scoped></style>
