<script setup lang="ts">
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import { authStore } from "@store/authStore";
import axios from "axios";
import { config } from "../config";
import { getCurrentInstance } from "vue";

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

const adminLogs = ref<any[]>([]);
const loadingFlag = ref(false);

const selectedShowType = ref<string[]>([]);

const selectedStartDate = ref<Date>(new Date("2020-01-01"));
const selectedEndDate = ref<Date>(new Date());

// mount
onMounted(async () => {
  await getAdminLogs();
  selectedShowType.value = ["重大", "注意", "普通"];
});

const getAdminLogs = async () => {
  try {
    loadingFlag.value = true;
    const response = await axios.get(`${config.BACKEND_URL}/admin_logs`, {
      headers: {
        Authorization: `Bearer ${authStore().getToken}`,
      },
    });

    // change date to local time (UTC+8)
    // add 8 hours to UTC time
    response.data.forEach((log: any) => {
      log["created_at"] = new Date(log["created_at"]);
      log["created_at"].setHours(log["created_at"].getHours() + 8);
    });

    adminLogs.value = response.data;

  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法取得使用紀錄", {});
    }
  }
  loadingFlag.value = false;
};

const filterLogs = () => {
  let filterResults = adminLogs.value.filter((log) => {
    return selectedShowType.value.includes(
      convertToShowType(log["type"])
  )});

  // filter by date
  if (selectedStartDate.value !== null) {
    filterResults = filterResults.filter((log) => {
      // only compare date part
      return new Date(log["created_at"]).setHours(0, 0, 0, 0) >= selectedStartDate.value.setHours(0, 0, 0, 0) && 
        new Date(log["created_at"]).setHours(0, 0, 0, 0) <= selectedEndDate.value.setHours(0, 0, 0, 0);
    });
  }

  return filterResults;
};

const convertToShowType = (type: string) => {
  if (type === "info") {
    return "普通";
  } else if (type === "warning") {
    return "注意";
  } else if (type === "critical") {
    return "重大";
  } else {
    return "未處理";
  }
};

const getTagColor = (type: string) => {
  if (type === "info") {
    return "primary";
  } else if (type === "warning") {
    return "warning";
  } else if (type === "critical") {
    return "error";
  } else {
    return "secondary";
  }
};

</script>

<template>
  <v-container class="mx-0 pa-7 mr-0">
    <v-row align="center" style="height: 100vh; width: 96vw">
      <v-col cols="3">
        <v-card class="side-bar pa-5" flat>
          <!-- icon btn: back to / -->
          <v-btn class="mb-3" variant="tonal" @click="() => {
            $router.push('/function_panel/3');
          }
            ">
            <v-icon>mdi-arrow-left</v-icon>
            返回目錄
          </v-btn>

          <v-container class="mt-5">
            <v-row align="center">
              <v-col align="center" cols="12">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw">
                  使用紀錄
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
                  <div>使用紀錄</div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <v-card-item>
            <v-container>
              <v-row>
                <v-col cols="4">
                  <v-date-input
                    v-model="selectedStartDate"
                    label="過濾初始日期"
                  ></v-date-input>
                </v-col>
                <v-col cols="4">
                  <v-date-input
                    v-model="selectedEndDate"
                    label="過濾結束日期"
                  ></v-date-input>
                </v-col>
                <v-col cols="4">
                  <v-select
                    v-model="selectedShowType"
                    chips
                    label="操作類型"
                    :items="['重大', '注意', '普通']"
                    multiple
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
            <v-card color="card_in_card" class="editor-content mb-3">
              <v-container>
                <v-row style="font-size: 0.8em">
                  <v-col cols="5" align="center"> 事件</v-col>
                  <v-col cols="2" align="center"> 使用者 </v-col>
                  <v-col cols="3" align="center"> 時間（UTC+8）</v-col>
                  <v-col cols="2" align="center"> 標籤 </v-col>
                </v-row>
                <v-divider class="my-2 mb-5"></v-divider>
                <v-row align="center" v-if="loadingFlag">
                  <v-col align="center">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </v-col>
                </v-row>
                <v-row align="center" v-for="(log, i) in filterLogs()" :key="i" style="font-size: 0.8em">
                  <v-divider v-if="i !== 0" class="my-2"></v-divider>
                  <v-col align="center">
                    <v-row align="center">
                      <v-col cols="5" align="center">
                        {{ log["message"] }}
                      </v-col>
                      <v-col cols="2" align="center">
                        {{ log["account"] }}
                      </v-col>
                      <v-col cols="3" align="center">
                        {{log["created_at"].toLocaleString() }}
                      </v-col>
                      <v-col cols="2" align="center">
                        <v-chip variant="flat" label :color="getTagColor(log['type'])">
                          {{ log["tag"] }}
                        </v-chip>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-card-item>
          <v-card-actions>
            <v-spacer></v-spacer>
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
