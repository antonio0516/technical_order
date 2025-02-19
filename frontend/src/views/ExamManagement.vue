<script setup lang="ts">
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import { authStore } from "@store/authStore";
import axios from "axios";
import { config } from "../config";
import { getCurrentInstance } from "vue";

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;



const HELICOPTER_TYPES = [
  "AH-1W", "OH-58D"
]

const selected_helicoper_type = ref(HELICOPTER_TYPES[0]);

const resetAllDialog = ref(false);
const startStudentId = ref(1);
const endStudentId = ref(60);

const students = ref<any[]>([]);

const currentPage = ref(0);

const entryLoadingFlag = ref(false);
const loading = ref(false);

const editExamTimeDialog = ref(false);
const editExamTimeSecond = ref(0);
const editExamTimeMinute = ref(0);
const editExamTimeHour = ref(0);
const currentExamTimeString = ref("loading...");
const currentExamTime = ref(0);


// mount
onMounted(async () => {
  await switchPage(0);
});

const switchPage = async (index: number) => {
  if (index == 0) {
    await getStudents();
  }
  else if (index == 1) {
    await getCurrentExamTime();
  }
  currentPage.value = index;
};

const openEditExamTimeDialog = async () => {
  editExamTimeDialog.value = true;
  editExamTimeSecond.value = currentExamTime.value % 60;
  editExamTimeMinute.value = Math.floor((currentExamTime.value % 3600) / 60);
  editExamTimeHour.value = Math.floor(currentExamTime.value / 3600);
};

const getCurrentExamTime = async () => {
  try {
    const response = await axios.get(`${config.BACKEND_URL}/exam_config/exam_time`, {
    });
    currentExamTime.value = response.data.exam_time;

    const hour = Math.floor(currentExamTime.value / 3600).toString().padStart(2, "0");
    const minute = Math.floor((currentExamTime.value % 3600) / 60).toString().padStart(2, "0");
    const second = (currentExamTime.value % 60).toString().padStart(2, "0");
    currentExamTimeString.value = `${hour}:${minute}:${second}`;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      console.log(error);
    }
  }
};

const timeLimitRange = (value: number) => {
  if (value < 0) {
    return 0;
  }
  else if (value > 59) {
    return 59;
  }
  return value;
}

const updateExamTime = async () => {
  try {
    loading.value = true;
    const totalSeconds = editExamTimeHour.value * 3600 + editExamTimeMinute.value * 60 + editExamTimeSecond.value;
    if (totalSeconds == 0) {
      $toast?.error("考試時間不能為 0 秒", {});
      loading.value = false;
      return;
    }
    const response = await axios.put(`${config.BACKEND_URL}/exam_config/exam_time`, {
      exam_time: totalSeconds,
    },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        }
      }
    );
    await getCurrentExamTime();
    $toast?.success("已更新考試時間");
    editExamTimeDialog.value = false;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法更新考試時間", {});
    }
  }
  loading.value = false;
};

const getStudents = async () => {
  try {
    entryLoadingFlag.value = true;
    const response = await axios.get(`${config.BACKEND_URL}/students`, {
      headers: {
        Authorization: `Bearer ${authStore().getToken}`,
      },
    });

    students.value = response.data;
    students.value.sort((a, b) => {
      return a["student_number"] - b["student_number"];
    });
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法取得學生資料", {});
    }
  }
  entryLoadingFlag.value = false;
};

const getScoreDocument = async () => {
  try {
    loading.value = true;

    const reponse = await axios({
      url: `${config.BACKEND_URL}/students/score_docx`,
      method: "GET",
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([reponse.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "成績文件.docx");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);

    $toast?.success("下載成功");
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法下載文件", {});
    }
  }
  loading.value = false;
};

const resetAllStudents = async () => {
  try {
    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/students/reset`,
      {
        start_number: startStudentId.value,
        end_number: endStudentId.value,
      },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getStudents();
    $toast?.success("已重置所有學生帳號");
    resetAllDialog.value = false;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法重置學生帳號", {});
    }
  }
  loading.value = false;
};

const resetSpecificStudent = async (id: string) => {
  try {
    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/students/reset/${id}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    await getStudents();
    $toast?.success("已重置學生帳號");
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法重置學生帳號", {});
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
  <v-dialog v-model="editExamTimeDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">編輯考試時間</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">考試時間（時：分：秒）</div>
        <v-container>
          <v-row>
            <v-col cols="4">
              <v-text-field class="input-remove-padding" readonly v-model="editExamTimeHour" variant="outlined"
                :hide-details="true" type="number"></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field class="input-remove-padding" readonly v-model="editExamTimeMinute" variant="outlined"
                :hide-details="true" type="number"></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field class="input-remove-padding" readonly v-model="editExamTimeSecond" variant="outlined"
                :hide-details="true" type="number"></v-text-field>
            </v-col>
          </v-row>
        </v-container>
        <div style="font-size: 1.2em">常見選項</div>
        <v-container>
          <v-row>
            <v-col cols="4">
              <v-container>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour - 1); }"
                      style="font-size:0.8em">
                      -1</v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour + 1); }"
                      style="font-size:0.8em">
                      +1
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour - 5); }"
                      style="font-size:0.8em">
                      -5
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour + 5); }"
                      style="font-size:0.8em">
                      +5
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour - 10); }"
                      style="font-size:0.8em">
                      -10
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeHour = timeLimitRange(editExamTimeHour + 10); }"
                      style="font-size:0.8em">
                      +10
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>
            <v-col cols="4">
              <v-container>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute - 1); }"
                      style="font-size:0.8em">
                      -1</v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute + 1); }"
                      style="font-size:0.8em">
                      +1
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute - 5); }"
                      style="font-size:0.8em">
                      -5
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute + 5); }"
                      style="font-size:0.8em">
                      +5
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute - 10); }"
                      style="font-size:0.8em">
                      -10
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeMinute = timeLimitRange(editExamTimeMinute + 10); }"
                      style="font-size:0.8em">
                      +10
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>
            <v-col cols="4">
              <v-container>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond - 1); }"
                      style="font-size:0.8em">
                      -1</v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond + 1); }"
                      style="font-size:0.8em">
                      +1
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond - 5); }"
                      style="font-size:0.8em">
                      -5
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond + 5); }"
                      style="font-size:0.8em">
                      +5
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond - 10); }"
                      style="font-size:0.8em">
                      -10
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn width="100%" color="primary"
                      @click="() => { editExamTimeSecond = timeLimitRange(editExamTimeSecond + 10); }"
                      style="font-size:0.8em">
                      +10
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>
          </v-row>
        </v-container>

      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large"
          :disabled="!(editExamTimeHour != 0 || editExamTimeMinute != 0 || editExamTimeSecond != 0)"
          @click="updateExamTime()">
          <span> 更新設置 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="resetAllDialog" width="auto" scrim="black">
    <v-card width="60vw" class="pa-5">
      <v-card-text>
        <div class="mb-10">
          注意：這將會刪除所有現有的學生資訊，並生出新的一批學生帳號。確定要重置所有學生資訊？
        </div>
        <v-text-field v-model="startStudentId" label="請輸入開始學號" outlined dense type="number"></v-text-field>
        <v-text-field v-model="endStudentId" label="請輸入開始學號" outlined dense type="number"></v-text-field>

      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" @click="resetAllDialog = false">取消</v-btn>
        <v-btn variant="outlined" color="error" @click="resetAllStudents">重置所有學生帳號</v-btn>
      </v-card-actions>
    </v-card>
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
              <v-col cols="12" class="pa-0 mb-1">
                <div class="class-title ma-0 pa-0">機型：</div>
              </v-col>

              <v-select v-model="selected_helicoper_type" :items="HELICOPTER_TYPES" outlined dense density="compact"
                variant="outlined"></v-select>

              <v-col align="center" cols="12">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw"
                  @click="() => { switchPage(0); }">
                  學員成績管理
                </v-btn>
              </v-col>

              <v-col align="center" cols="12">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw"
                  @click="() => { switchPage(1); }">
                  考試相關設置
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
                  <div>學員成績管理</div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <v-card-item>
            <v-card color="card_in_card" class="editor-content mb-3">
              <v-container>
                <v-row style="font-size: 0.8em">
                  <v-col cols="3" align="center"> 學號（帳號） </v-col>
                  <v-col cols="3" align="center"> 密碼 </v-col>
                  <v-col cols="3" align="center"> 成績 </v-col>
                  <v-col cols="3" align="center"> 可用操作 </v-col>
                </v-row>
                <v-divider class="my-2 mb-5"></v-divider>
                <v-row align="center" v-if="entryLoadingFlag">
                  <v-col align="center">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </v-col>
                </v-row>
                <v-row align="center" v-for="(student, i) in students" :key="i" style="font-size: 0.8em">
                  <v-divider v-if="i !== 0" class="my-2"></v-divider>
                  <v-col align="center">
                    <v-row align="center">
                      <v-col cols="3" align="center">
                        {{ student["student_number"] }}
                      </v-col>
                      <v-col cols="3" align="center">{{
                        student["password"]
                        }}</v-col>
                      <v-col cols="3" align="center">
                        <div v-if="student['grade'][selected_helicoper_type] != -1">
                          {{ student['grade'][selected_helicoper_type] }}
                        </div>
                        <div v-else>
                          尚未評分
                        </div>
                      </v-col>
                      <v-col cols="3">
                        <v-btn class="" color="error" variant="outlined" @click="resetSpecificStudent(student['_id'])">
                          重置帳號
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
            <!-- <a :href="`${config.BACKEND_URL}/students/score_docx`" download="成績文件.docx"> -->
            <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em" @click="getScoreDocument">
              下載成績文件
            </v-btn>
            <v-btn color="primary" class="ml-7 mr-5" variant="flat" size="large" style="font-size: 0.75em"
              @click="async () => { await getStudents() }">
              重新整理
            </v-btn>
            <v-btn color="error" class="mr-5" variant="flat" size="large" style="font-size: 0.75em"
              @click="resetAllDialog = true">
              重置所有學生帳號
            </v-btn>
          </v-card-actions>
        </v-card>
        <v-card class="main-content pa-5 pt-2" flat v-if="currentPage === 1">
          <div class="py-0 pt-0">
            <v-container>
              <v-row>
                <v-col>
                  <div>考試相關設置</div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <v-card-item>
            <v-card color="card_in_card" class="editor-content mb-3">
              <v-container>
                <v-row style="font-size: 0.8em">
                  <v-col cols="4" align="center"> 欄位 </v-col>
                  <v-col cols="4" align="center"> 當前數值 </v-col>
                  <v-col cols="4" align="center"> 可用操作 </v-col>
                </v-row>
                <v-divider class="my-2 mb-5"></v-divider>
                <v-row align="center" style="font-size: 0.8em">
                  <v-col align="center">
                    <v-row align="center">
                      <v-col cols="4" align="center">
                        考試時間（時：分：秒）
                      </v-col>
                      <v-col cols="4" align="center">
                        {{ currentExamTimeString }}
                      </v-col>
                      <v-col cols="4">
                        <v-btn icon class="mb-2 ml-3" color="primary" flat
                          @click="async () => { await openEditExamTimeDialog() }">
                          <v-icon>mdi-file-document-edit-outline</v-icon>
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-card-item>
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
