<script setup lang="ts">
import { ref } from "vue";
import { rules } from "@/library/inputRules";
import { config } from "@/config";
import axios from "axios";

// toast
import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

let step = ref(1);

let accountInput = ref("");
let passwordInput = ref("");
let checkPasswordInput = ref("");
let questionInput = ref("排序最要好的五個朋友？");
let answerInput = ref("");

let form1: any = ref(null);
let form2: any = ref(null);

const clearInput = () => {
  accountInput.value = "";
  passwordInput.value = "";
  checkPasswordInput.value = "";
  questionInput.value = "排序最要好的五個朋友？";
  answerInput.value = "";
};

const emits = defineEmits(["switchAuthView"]);

const register = async () => {
  const { valid } = await form2.value.validate();
  if (!valid) return;

  const data = {
    account: accountInput.value,
    password: passwordInput.value,
    safe_question: questionInput.value,
    safe_answer: answerInput.value,
  };

  const res = await axios
    .post(`${config.BACKEND_URL}/auth/register`, data)
    .then((res) => {
      console.log(res);
      if (res.status === 201) {
        emits("switchAuthView", "login");
        toast.success("註冊成功", {});
      }
    })
    .catch((err) => {
      console.log(err);
      if (err.response.status === 400 || err.response.status === 409) {
        toast.error(err.response.data.detail, {});
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
        <div style="font-size: 1.5em">註冊頁面</div>
        <!-- step 1 -->
        <v-form ref="form1" v-if="step === 1">
          <div class="mt-5">
            <v-text-field
              density="compact"
              label="帳號（學號）"
              type="input"
              variant="outlined"
              v-model="accountInput"
              :rules="[
                rules.required,
                rules.accountLength,
                rules.englishAndNumber,
              ]"
              class="mb-2"
            >
            </v-text-field>
            <v-text-field
              density="compact"
              label="密碼"
              type="password"
              variant="outlined"
              class="mb-2"
              :rules="[
                rules.required,
                rules.passwordLength,
                rules.englishAndNumber,
              ]"
              v-model="passwordInput"
            >
            </v-text-field>
            <v-text-field
              density="compact"
              label="再次輸入密碼"
              class="mb-3"
              :rules="[
                rules.required,
                rules.passwordLength,
                rules.englishAndNumber,
                rules.checkPassword(passwordInput, checkPasswordInput),
              ]"
              type="password"
              variant="outlined"
              v-model="checkPasswordInput"
            >
            </v-text-field>
          </div>
          <v-btn
            width="100%"
            :rounded="true"
            color="primary"
            @click=""
            type="submit"
          >
            下一步
          </v-btn>
        </v-form>
        <v-form v-if="step === 2" ref="form2">
          <div class="my-3 mb-5" style="font-size: 0.95em">
            該答案將在忘記密碼時用以確認身分，效力等同第二個密碼，切勿設計過於簡單的問答。
          </div>
          <div class="mt-3">
            <v-text-field
              class="mb-2"
              density="compact"
              label="請設置安全性問題"
              hint="範例：最要好的三個朋友？"
              persistent-hint
              :rules="[rules.required, rules.safeProblemLength]"
              type="input"
              variant="outlined"
              v-model="questionInput"
            >
            </v-text-field>
            <v-text-field
              class="my-2 mt-5"
              density="compact"
              label="安全性問題回答"
              type="input"
              :rules="[rules.required, rules.safeAnswerLength]"
              variant="outlined"
              v-model="answerInput"
            >
            </v-text-field>
            <v-spacer></v-spacer>
            <v-container>
              <v-row justify="space-between">
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="secondary"
                  @click="step--"
                >
                  上一步
                </v-btn>
                <v-btn
                  width="45%"
                  :rounded="true"
                  color="primary"
                  @click="register"
                >
                  註冊
                </v-btn>
              </v-row>
            </v-container>
          </div>
        </v-form>
        <div class="text-right mt-2"></div>
        <div class="text-right mt-3">
          <v-btn
            variant="outlined"
            width="100%"
            :rounded="true"
            color="secondary"
            @click="
              clearInput();
              $emit('switchAuthView', 'login');
            "
          >
            登入
          </v-btn>
        </div>
      </v-card>
    </v-row>
  </v-container>
</template>

<style scoped></style>
