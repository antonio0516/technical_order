<script setup lang="ts">
import { ref, reactive } from "vue";
import { onMounted } from "vue";

import axios from "axios";
import { config } from "@/config";
import { authStore } from "@store/authStore";
import { useTagStore } from "@store/tagStore";
import { getCurrentInstance } from "vue";

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

const newTagName = ref("");
let editTagData = reactive({
  _id: "",
  name: "",
});


const newTagDialog = ref(false);
const editTagDialog = ref(false);
const deleteTagDialog = ref(false);

const tagStore = useTagStore();

const deleteTagId = ref("");

const loading = ref(false);

const addNewTag = async () => {
  try {
    loading.value = true;
    console.log(`${config.BACKEND_URL}/technical_orders/tags`);
    await tagStore.addTag(newTagName.value);
    newTagName.value = "";
    newTagDialog.value = false;
    $toast?.success("新增標籤成功", {});
  } catch (error: any) {
    try {
      $toast?.error(error.response.data.detail, {});
      console.error(error);
    }
    catch {
      $toast?.error("後臺發生錯誤，新增標籤失敗", {});
    }
  }
  loading.value = false;
};

// mount
onMounted(async () => {
  await tagStore.updateTagItems();
});

const openDeleteTagDialog = (id: string) => {
  deleteTagId.value = id;
  deleteTagDialog.value = true;
};

const deleteTag = async (id: string) => {
  try {
    loading.value = true;
    await tagStore.deleteTag(id);
    $toast?.success("刪除標籤成功", {});
    deleteTagDialog.value = false;
  } catch (error: any) {
    try {
      $toast?.error(error.response.data.detail, {});
      console.error(error);
    }
    catch {
      $toast?.error("後臺發生錯誤，刪除標籤失敗", {});
    }
  }
  loading.value = false;
};

const updateTag = async () => {
  const id = editTagData._id;
  const name = editTagData.name;

  try {
    loading.value = true;
    await tagStore.updateTag(id, name);
    editTagDialog.value = false;
    $toast?.success("更新標籤成功", {});
  } catch (error: any) {
    try {
      $toast?.error(error.response.data.detail, {});
      console.error(error);
    }
    catch {
      $toast?.error("後臺發生錯誤，更新標籤失敗", {});
    }
  }
  loading.value = false;
};

const openEditTagDialog = (item: any) => {
  editTagData._id = item._id;
  editTagData.name = item.name;
  editTagDialog.value = true;
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
  <v-dialog v-model="deleteTagDialog" width="auto" scrim="black">
    <v-card width="40vw" height="" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">刪除標籤</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">確定要刪除此標籤嗎？</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" color="primary_lighter" variant="outlined" size="large" @click="deleteTagDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn color="error" variant="outlined" size="large" @click="async () => {
    await deleteTag(deleteTagId);
    deleteTagDialog = false;
  }">
          <span> 刪除 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="newTagDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">新增標籤</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="newTagName" outlined dense clearable class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="addNewTag" :disabled="newTagName === ''">
          <span> 新增 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editTagDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">編輯標籤</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="editTagData.name" outlined dense clearable class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="updateTag()">
          <span> 更新 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-card class="main-content pa-5 pt-2" flat>
    <div class="py-0 pt-0">
      <v-container>
        <v-row>
          <v-col>
            <div>標籤編輯頁面</div>
          </v-col>
        </v-row>
      </v-container>
    </div>
    <v-card-item>
      <v-card color="card_in_card" class="editor-content mb-3">
        <v-container>
          <v-row style="font-size: 0.8em">
            <v-col cols="8" align="center"> 名稱 </v-col>
            <v-col cols="4" align="center"> 可用操作 </v-col>
            <v-divider class="my-2 mb-5"></v-divider>
          </v-row>
          <v-row align="center" v-if="tagStore.entryLoading">
            <v-col align="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>

          <v-row align="center" v-for="(item, i) in tagStore.tags" :key="i" style="font-size: 0.8em">
            <v-divider v-if="i !== 0" class="my-2"></v-divider>
            <v-col align="center">
              <v-row align="center">
                <v-col cols="8" align="center">{{ item.name }}</v-col>
                <v-col cols="4">
                  <v-btn icon class="mb-2" color="primary" flat @click="openEditTagDialog(item)">
                    <v-icon>mdi-file-document-edit-outline</v-icon>
                  </v-btn>
                  <v-btn icon class="mb-2 ml-3" color="error" flat @click="openDeleteTagDialog(item._id)">
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
      <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em" @click="newTagDialog = true">
        新增
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style>
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

.input-remove-padding .v-field__input {
  padding-top: 0px;
  padding-bottom: 0px;
  font-size: 1.4em;
}
</style>
