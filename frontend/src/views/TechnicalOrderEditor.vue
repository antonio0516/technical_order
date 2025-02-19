<script setup lang="ts">
import AuthCard from "@/components/LoginRegister/AuthCard.vue";
import MainClass from "@/components/TechnicalOrderEditor/MainClass.vue";
import SubClass from "@/components/TechnicalOrderEditor/SubClass.vue";
import OrderTemplate from "@/components/TechnicalOrderEditor/OrderTemplate.vue";
import TechnicalOrder from "@/components/TechnicalOrderEditor/TechnicalOrder.vue";
import Tag from "@/components/TechnicalOrderEditor/Tag.vue";
import { useMainClassStore } from "@store/mainClassStore";
import { useTechnicalOrderStore } from "@store/TechnicalOrderStore";
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import axios from "axios";
import { config } from "@/config";
import { authStore } from "@store/authStore";
import { useTagStore } from "@store/tagStore";
import { getCurrentInstance } from "vue";

// console.log(import.meta.env.VITE_APP_TITLE);
const appTitle = "技令編輯器";

const saveVersionDialog = ref(false);
const saveVersionName = ref("");

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

const currentPage = ref<string>("manual"); // manual, mainClass, subClass, template

let mainClassList = reactive<any[]>([]);

const loading = ref(false);

const mainClassStore = useMainClassStore();
const technicalOrderStore = useTechnicalOrderStore();
const tagStore = useTagStore();

watch(
  () => mainClassStore.getItems,
  (newVal) => {
    Object.assign(mainClassList, mainClassStore.getItems);
  }
);

watch(
  () => mainClassStore.getSubClasses,
  (newVal) => {
    mainClassStore.subClasses = newVal;
  }
);




// mount
onMounted(async () => {
  mainClassList.unshift({
    _id: "all",
    name: "全部",
  });
  const mainClassStore = useMainClassStore();
  await mainClassStore.init();
  Object.assign(mainClassList, mainClassStore.getItems);
  // add empty item for select all
  mainClassList.unshift({
    _id: "all",
    name: "全部",
  });

  // mainClassStore.subClasses.unshift({
  //   main_class: "all",
  //   sub_class: "全部",
  // });

  await tagStore.updateTagItems();
});

const onSelectedMainClassChange = async (newMainClassId: string) => {
  if (newMainClassId === "all") {
    console.log("I really want to select all");
    mainClassStore.subClasses = [
      {
        main_class: "all",
        sub_class: "全部",
      },
    ];
    mainClassStore.selectedSubClass.sub_class = "全部";
  }
  await mainClassStore.selectMainClass(newMainClassId);
  await get_filter_result(newMainClassId);
  mainClassStore.selectedSubClass.sub_class = "全部";
  // technicalOrderStore.resetRenderIndexLimit();
};

const onSelectedTagChange = (newTagIdList: any) => {
  // technicalOrderStore.resetRenderIndexLimit();
};

const onSelectedSubClassChange = (newSubClass: string) => {
  // technicalOrderStore.resetRenderIndexLimit();
  // console.log(newSubClass);
  // console.log(newName);
  // get_filter_result();
};

const get_filter_result = async (newMainClassId: string) => {
  // console.log(mainClass, subClass);
  const mainClassStore = useMainClassStore();
  await mainClassStore.updateSubClasses(newMainClassId);
  // const newSubClassesList = await mainClassStore.getSubClasses;

  // mainClassStore.subClasses = newSubClassesList;
};

const saveCurrentVersion = async () => {
  try {
    loading.value = true;
    const response = await axios.post(
      `${config.BACKEND_URL}/technical_orders/versions`,
      {
        version_name: saveVersionName.value,
      },
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    $toast?.success("已儲存技令版本");
    saveVersionDialog.value = false;
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法儲存版本", {});
    }
  }
  loading.value = false;
};
</script>

<template>
  <v-dialog v-model="loading" persistent fullscreen content-class="loading-dialog" scrim="black">
    <v-container>
      <v-row align="center" justify="center" style="height: 100vh">
        <div style="display: flex; flex-direction: column; align-items: center;">
          <v-progress-circular class="mb-5" indeterminate :size="70" :width="7" color="primary"></v-progress-circular>
          <div class="text-h4">Loading...</div>
        </div>
      </v-row>
    </v-container>
  </v-dialog>
  <v-dialog v-model="saveVersionDialog" width="auto" scrim="black">
    <v-card width="60vw" class="pa-5">
      <v-card-text>
        <div class="mb-10">
          按下按鈕後，將會將當前的所有技令資料單獨儲存成可復原的版本
        </div>
        <v-text-field v-model="saveVersionName" label="請輸入版本命名" outlined dense></v-text-field>

      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" @click="saveVersionDialog = false">取消</v-btn>
        <v-btn :disabled="!saveVersionName" variant="outlined" color="primary_lighter"
          @click="saveCurrentVersion">儲存技令版本</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-container class="mx-0 pa-7 mr-0">
    <v-row align="center" style="height: 100vh; width: 96vw">
      <v-col cols="3">
        <v-card class="side-bar pa-5" flat style="overflow-y: scroll;">
          <!-- icon btn: back to / -->
          <v-btn class="mb-3" variant="tonal" @click="() => {
    $router.push('/function_panel/0');
  }
    ">
            <v-icon>mdi-arrow-left</v-icon>
            返回目錄
          </v-btn>
          <div v-if="currentPage == 'manual' || currentPage == 'subClass'">
            <div class="class-title mb-1">主目錄：</div>
            <v-select density="compact" :items="mainClassStore.getItemsWithAll" item-title="name" item-value="_id"
              variant="outlined" v-model="mainClassStore.selectedMainClass._id"
              @update:modelValue="onSelectedMainClassChange" />
          </div>
          <div v-if="currentPage == 'manual'">
            <div class="class-title mb-1">次目錄：</div>
            <v-select density="compact" :items="mainClassStore.filterSubClasses" item-title="sub_class"
              item-value="sub_class" variant="outlined" v-model="mainClassStore.selectedSubClass.sub_class"
              @update:modelValue="onSelectedSubClassChange" />
          </div>

          <div v-if="currentPage == 'manual'">
            <!-- make slection check box small -->
            <div class="class-title mb-1">標籤：</div>
            <v-select dense :items="tagStore.tags" item-title="name" item-value="_id" chips variant="outlined"
              v-model="tagStore.selectedTags" multiple clearable style="font-size: 5.8em !important;"
              @update:modelValue="onSelectedTagChange"></v-select>
          </div>

          <v-container class="mt-0">
            <v-row align="center">
              <v-col align="center" cols="12" v-if="currentPage != 'manual'">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw" @click="async () => {
    await tagStore.updateTagItems();
    currentPage = 'manual';
  }
    ">
                  編輯技令
                </v-btn>
              </v-col>
              <v-col align="center" cols="12" v-if="currentPage != 'mainClass'">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw" @click="() => {
    currentPage = 'mainClass';
  }
    ">
                  編輯主目錄
                </v-btn>
              </v-col>
              <v-col align="center" cols="12" v-if="currentPage != 'subClass'">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw" @click="() => {
    currentPage = 'subClass';
  }
    ">
                  編輯次目錄
                </v-btn>
              </v-col>
              <v-col align="center" cols="12" v-if="currentPage != 'tag'">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw" @click="() => {
    currentPage = 'tag';
  }
    ">
                  編輯標籤
                </v-btn>
              </v-col>
              <v-col align="center" cols="12" v-if="currentPage != 'template'">
                <v-btn color="secondary" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw" @click="() => {
    currentPage = 'template';
  }
    ">
                  編輯技令欄位
                </v-btn>
              </v-col>
              <v-col align="center" cols="12" v-if="currentPage != 'template'">
                <v-btn color="primary_lighter" variant="outlined" size="large" style="font-size: 0.7em; width: 16vw"
                  @click="() => {
    saveVersionDialog = true;
  }">
                  儲存當前技令版本
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
      <v-col>
        <main-class v-if="currentPage == 'mainClass'" />
        <sub-class v-if="currentPage == 'subClass'" />
        <order-template v-if="currentPage == 'template'" />
        <!-- pass mainClass and subClass -->
        <technical-order v-if="currentPage == 'manual'" :selected-main-class-id="mainClassStore.selectedMainClass._id"
          :selected-sub-class="mainClassStore.selectedSubClass.sub_class" :selected-tags="tagStore.selectedTags" />
        <tag v-if="currentPage == 'tag'" />
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
<style>
.v-list-item__prepend {
  display: none;
}
</style>