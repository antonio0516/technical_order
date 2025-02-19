<script setup lang="ts">
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import { authStore } from "@store/authStore";
import { rules } from "@/library/inputRules";
import axios from "axios";
import { config } from "../config";
import { getCurrentInstance } from "vue";

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

const accounts = ref<any[]>([]);

const currentPage = ref(0);

const entryLoadingFlag = ref(false);
const loading = ref(false);

const resetPasswordDialog = ref(false);
const resetAccountString = ref("");
const resetNewPassword = ref("");
const resetNewPasswordCheck = ref("");

const deleteAccountDialog = ref(false);
const deleteAccountString = ref("");

const newAccountDialog = ref(false);
const newAccount = ref("");
const newAccountPassword = ref("");
const newAccountPasswordCheck = ref("");

let formRegister: any = ref(null);
let formResetPassword: any = ref(null);

// mount
onMounted(async () => {
  await switchPage(0);
});

const switchPage = async (index: number) => {
  if (index == 0) {
    await getAdminAccounts();
  }
  currentPage.value = index;
};

const getAdminAccounts = async () => {
  try {
    entryLoadingFlag.value = true;
    const response = await axios.get(`${config.BACKEND_URL}/auth/accounts`, {
      headers: {
        Authorization: `Bearer ${authStore().getToken}`,
      },
    });

    accounts.value = response.data.accounts;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法取得管理員資料", {});
    }
  }
  entryLoadingFlag.value = false;
};

const createNewAccount = async (account: string, password: string) => {
  try {
    const { valid } = await formRegister.value.validate();
    if (!valid) return;

    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/auth/register`,
      {
        account: account,
        password: password,
      },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getAdminAccounts();
    $toast?.success("已新增帳號");
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法新增帳號", {});
    }
  }
  loading.value = false;
  newAccountDialog.value = false;
};

const resetPassword = async (account: string, newPassword: string) => {
  try {
    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/auth/reset_password`,
      {
        account: account,
        password: newPassword,
      },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    $toast?.success("已重設 " + account + " 的密碼");
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法重置密碼", {});
    }
  }
  loading.value = false;
  resetPasswordDialog.value = false;
};

const deleteAccount = async (account: string) => {
  try {
    loading.value = true;
    const response = await axios.delete(
      `${config.BACKEND_URL}/auth/${account}`,
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getAdminAccounts();
    $toast?.success("已刪除 " + account + " 的帳號");
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法刪除帳號", {});
    }
  }
  loading.value = false;
  deleteAccountDialog.value = false;
};

const openNewAccountDialog = () => {
  newAccount.value = "";
  newAccountPassword.value = "";
  newAccountPasswordCheck.value = "";
  newAccountDialog.value = true;
};

const openDeleteAccountDialog = (account: string) => {
  deleteAccountString.value = account;
  deleteAccountDialog.value = true;
};

const openResetPasswordDialog = (account: string) => {
  resetAccountString.value = account;
  resetNewPassword.value = "";
  resetNewPasswordCheck.value = "";
  resetPasswordDialog.value = true;
};
</script>

<template>
  <v-dialog v-model="loading" persistent fullscreen content-class="loading-dialog" overlay-color="black" scrim="black">
    <v-container>
      <v-row align="center" justify="center" style="height: 100vh">
        <div style="display: flex; flex-direction: column; align-items: center;">
          <v-progress-circular class="mb-5" indeterminate :size="70" :width="7" color="primary"></v-progress-circular>
          <div class="text-h4">Loading...</div>
        </div>
      </v-row>
    </v-container>
  </v-dialog>
  <v-dialog v-model="newAccountDialog" persistent max-width="400" content-class="dialog" overlay-color="black" width="auto" scrim="black">
    <v-form ref="formRegister">
      <v-card width="30vw" height="70vh" class="pa-5 ml-10">
        <v-card-title>新增帳號</v-card-title>
        <v-card-text>
          <v-text-field v-model="newAccount" label="帳號" dense
            class="mt-5"
            :rules="[
              rules.required,
              rules.accountLength,
              rules.englishAndNumber,
            ]"></v-text-field>
          <v-text-field v-model="newAccountPassword" label="密碼" dense
            class="mt-5"
            type="password"
            :rules="[
              rules.required,
              rules.passwordLength,
              rules.englishAndNumber,
            ]"
          ></v-text-field>
          <v-text-field v-model="newAccountPasswordCheck" label="確認密碼" dense
            class="mt-5"
            type="password"
            :rules="[
              rules.required,
              rules.passwordLength,
              rules.englishAndNumber,
              rules.checkPassword(newAccountPassword, newAccountPasswordCheck),
            ]"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" color="primary_lighter" @click="newAccountDialog = false">取消</v-btn>
          <v-btn variant="flat" class="ml-5" color="primary" @click="createNewAccount(newAccount, newAccountPassword)">新增</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
  <v-dialog v-model="deleteAccountDialog" persistent max-width="400" content-class="dialog" overlay-color="black" width="auto" scrim="black">
    <v-card width="30vw" height="70vh" class="pa-5 ml-10">
      <v-card-title>刪除帳號</v-card-title>
      <v-card-text>
        <div>確定要刪除 {{ deleteAccountString }} 的帳號嗎？</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" color="primary_lighter" @click="deleteAccountDialog = false">取消</v-btn>
        <v-btn variant="flat" class="ml-5" color="error" @click="deleteAccount(deleteAccountString)">刪除</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="resetPasswordDialog" persistent max-width="400" content-class="dialog" overlay-color="black" width="auto" scrim="black">
    <v-form ref="formResetPassword">
      <v-card width="30vw" height="70vh" class="pa-5 ml-10">
        <v-card-title>重設密碼</v-card-title>
        <v-card-text>
          <div>帳號：{{ resetAccountString }}</div>
          <v-text-field v-model="resetNewPassword" label="新密碼" dense
            class="mt-5"
            type="password"
            :rules="[
              rules.required,
              rules.passwordLength,
              rules.englishAndNumber,
            ]"
          ></v-text-field>
          <v-text-field v-model="resetNewPasswordCheck" label="確認新密碼" dense
            class="mt-5"
            type="password"
            :rules="[
              rules.required,
              rules.passwordLength,
              rules.englishAndNumber,
              rules.checkPassword(resetNewPassword, resetNewPasswordCheck),
            ]"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" color="primary_lighter" @click="resetPasswordDialog = false">取消</v-btn>
          <v-btn variant="flat" class="ml-5" color="primary" @click="resetPassword(resetAccountString, resetNewPassword)">重設</v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
    </v-dialog>
  <v-container class="mx-0 pa-7 mr-0">
    <v-row align="center" style="height: 100vh; width: 96vw">
      <v-col cols="3">
        <v-card class="side-bar pa-5" flat>
          <!-- icon btn: back to / -->
          <v-btn class="mb-3" variant="tonal" @click="() => {
            $router.push('/function_panel/1');
          }
            ">
            <v-icon>mdi-arrow-left</v-icon>
            返回目錄
          </v-btn>

          <v-container class="mt-5">
            <v-row align="center">
              <v-col align="center" cols="12">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw"
                  @click="() => { switchPage(0); }">
                  管理員帳號管理
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="main-content pa-5 pt-2" flat v-if="currentPage === 0">
          <div class="py-0 pt-0">
            <v-container>
              <v-row>
                <v-col>
                  <div>管理員帳號管理</div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <v-card-item>
            <v-card color="card_in_card" class="editor-content mb-3">
              <v-container>
                <v-row style="font-size: 0.8em">
                  <v-col cols="6" align="center"> 帳號 </v-col>
                  <v-col cols="6" align="center"> 可用操作 </v-col>
                </v-row>
                <v-divider class="my-2 mb-5"></v-divider>
                <v-row align="center" v-if="entryLoadingFlag">
                  <v-col align="center">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </v-col>
                </v-row>
                <v-row align="center" v-for="(account, i) in accounts" :key="i" style="font-size: 0.8em">
                  <v-divider v-if="i !== 0" class="my-2"></v-divider>
                  <v-col align="center">
                    <v-row align="center">
                      <v-col cols="6" align="center">
                        {{ account }}
                      </v-col>
                      <v-col cols="6">
                        <v-btn class="" color="primary_lighter" variant="outlined" @click="openResetPasswordDialog(account)">
                          重設密碼
                        </v-btn>
                        <v-btn class="ml-5" color="error" variant="outlined" @click="openDeleteAccountDialog(account)" v-if="account !== 'admin'">
                          刪除帳號
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-card-item>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" class="ml-7 mr-5" variant="flat" size="large" style="font-size: 0.75em"
              @click="async () => { await getAdminAccounts() }">
              重新整理
            </v-btn>
            <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em" @click="openNewAccountDialog">
              新增帳號
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.side-bar {
  width: 100%;
  height: 80vh;
}

.main-content {
  width: auto;
  height: 80vh;
}

.editor-content {
  width: 100%;
  height: 53vh;
  overflow-y: scroll;
  overflow-x: hidden;

  font-size: 0.8em;
}

.class-title {
  font-size: 1em;
}

.input-remove-padding .v-field__input {
  padding-top: 0px;
  padding-bottom: 0px;
  font-size: 2.5em;
}
</style>
