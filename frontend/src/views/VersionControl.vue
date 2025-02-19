<script setup lang="ts">
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import { authStore } from "@store/authStore";
import axios from "axios";
import { config } from "../config";
import { getCurrentInstance } from "vue";
import { useMainClassStore } from "@store/mainClassStore";

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;


const deleteVersionDialog = ref(false);
const restoreVersionDialog = ref(false);
const startStudentId = ref(1);
const endStudentId = ref(60);

const versions = ref<any[]>([]);

const deleteVersionName = ref("");
const deleteVersionId = ref("");
const restoreVersionName = ref("");
const restoreVersionId = ref("");

const loading = ref(false);

const entryLoadingFlag = ref(false);

const mainClassStore = useMainClassStore();

// mount
onMounted(async () => {
  await getVersions();
  console.log(versions.value);
});

const getVersions = async () => {
  try {
    entryLoadingFlag.value = true;
    const response = await axios.get(`${config.BACKEND_URL}/technical_orders/versions`, {
      headers: {
        Authorization: `Bearer ${authStore().getToken}`,
      },
    });

    versions.value = response.data;
    versions.value.sort((a, b) => {
      return a["created_at"] - b["created_at"];
    });
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法取得版本資料", {});
    }
  }
  entryLoadingFlag.value = false;
};

const deleteSelectVersion = async () => {
  try {
    loading.value = true;
    const response = await axios.delete(
      `${config.BACKEND_URL}/technical_orders/versions/${deleteVersionId.value}`,
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getVersions();
    $toast?.success("已刪除版本");
    deleteVersionDialog.value = false;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法刪除版本", {});
    }
  }
  loading.value = false;
};

const restoreSelectVersion = async () => {
  try {
    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/technical_orders/versions/restore/${restoreVersionId.value}`,
      {
        version_id: restoreVersionId.value,
      },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getVersions();
    await mainClassStore.selectMainClass("all");
    mainClassStore.selectedSubClass.sub_class = "全部";

    $toast?.success("已還原版本");
    restoreVersionDialog.value = false;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法還原版本", {});
    }
  }
  loading.value = false;
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
  <v-dialog v-model="deleteVersionDialog" width="auto" scrim="black">
    <v-card width="60vw" class="pa-5">
      <v-card-text>
        <div class="mb-10">
          該操作不可復原，確定要刪除 {{ deleteVersionName }} 嗎？
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" @click="deleteVersionDialog = false">取消</v-btn>
        <v-btn class="ml-5" variant="outlined" color="error" @click="deleteSelectVersion">刪除該版本</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="restoreVersionDialog" width="auto" scrim="black">
    <v-card width="60vw" class="pa-5">
      <v-card-text>
        <div class="mb-10">
          <div>
            該操作會覆蓋當前的技令資料，建議將當前版本先行儲存。
          </div>
          <div>
            確定要還原 {{ restoreVersionName }} 嗎？
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" @click="restoreVersionDialog = false">取消</v-btn>
        <v-btn class="ml-5" variant="outlined" color="primary_lighter" @click="restoreSelectVersion">還原該版本</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-container class="mx-0 pa-7 mr-0">
    <v-row align="center" style="height: 100vh; width: 96vw">
      <v-col cols="3">
        <v-card class="side-bar pa-5" flat>
          <!-- icon btn: back to / -->
          <v-btn class="mb-3" variant="tonal" @click="() => {
    $router.push('/function_panel/2');
  }
    ">
            <v-icon>mdi-arrow-left</v-icon>
            返回目錄
          </v-btn>

          <v-container class="mt-5">
            <v-row align="center">
              <v-col align="center" cols="12">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw">
                  版本紀錄
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="main-content pa-5 pt-2" flat>
          <div class="py-0 pt-0">
            <v-container>
              <v-row>
                <v-col>
                  <div>版本紀錄</div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <v-card-item>
            <v-card color="card_in_card" class="editor-content mb-3">
              <v-container>
                <v-row style="font-size: 0.8em">
                  <v-col cols="6" align="center"> 版本命名</v-col>
                  <v-col cols="3" align="center"> 創建時間 </v-col>
                  <v-col cols="3" align="center"> 可用操作 </v-col>

                </v-row>
                <v-divider class="my-2 mb-5"></v-divider>
                <v-row align="center" v-if="entryLoadingFlag">
                  <v-col align="center">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </v-col>
                </v-row>
                <v-row align="center" v-for="(version, i) in    versions   " :key="i" style="font-size: 0.8em">
                  <v-divider v-if="i !== 0" class="my-2"></v-divider>
                  <v-col align="center">
                    <v-row align="center">
                      <v-col cols="6" align="center">
                        {{ version["version_name"] }}
                      </v-col>
                      <v-col cols="3" align="center">{{
    version["created_at"]
  }}</v-col>
                      <v-col cols="3" align="center">
                        <v-btn icon class="mb-2 ml-3" color="primary" flat @click="() => {
      restoreVersionId = version['_id'];
      restoreVersionName = version['version_name'];
      restoreVersionDialog = true;
    }">
                          <v-icon>mdi-restore</v-icon>
                        </v-btn>
                        <v-btn icon class="mb-2 ml-3" color="error" flat @click="() => {
    deleteVersionId = version['_id'];
    deleteVersionName = version['version_name'];
    deleteVersionDialog = true;
  }">
                          <v-icon>mdi-delete</v-icon>
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
            <!-- <v-btn icon class="mb-2 ml-3" color="error" flat @click="">
              <v-icon>mdi-delete</v-icon>
            </v-btn> -->
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
</style>
