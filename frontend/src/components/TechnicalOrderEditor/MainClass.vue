<script setup lang="ts">
import { ref, reactive } from "vue";
import { useMainClassStore } from "@store/mainClassStore";
import { onMounted } from "vue";

const items: any = ref<any[]>([]);

const newClassname = ref("");
let editMainClassData = reactive({
  _id: "",
  name: "",
});

const newClassDialog = ref(false);
const editClassDialog = ref(false);
const deleteClassDialog = ref(false);

const deleteMainClassId = ref("");
const mainClassStore = useMainClassStore();

const loading = ref(false);

const addNewMainClass = async () => {
  loading.value = true;
  const success = await mainClassStore.addItem(newClassname.value);
  loading.value = false;
  if (success) {
    await mainClassStore.init();
    items.value = mainClassStore.getItems;
    newClassname.value = "";
    newClassDialog.value = false;
  }
  
};

// mount
onMounted(async () => {
  await mainClassStore.init();
  items.value = mainClassStore.getItems;
});

const deleteMainClass = async (id: string) => {
  loading.value = true;
  const success = await mainClassStore.deleteItem(id);
  loading.value = false;
  if (success) {
    await mainClassStore.init();
    items.value = mainClassStore.getItems;
  }
};

const updateMainClass = async () => {
  const id = editMainClassData._id;
  const name = editMainClassData.name;

  loading.value = true;
  const success = await mainClassStore.updateItem(id, name);
  loading.value = false;
  if (success) {
    await mainClassStore.init();
    items.value = mainClassStore.getItems;
    editClassDialog.value = false;
  }
};

const openEditMainClassDialog = (item: any) => {
  editMainClassData._id = item._id;
  editMainClassData.name = item.name;
  editClassDialog.value = true;
};

const openDeleteMainClassDialog = (id: string) => {
  deleteMainClassId.value = id;
  deleteClassDialog.value = true;
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
  <v-dialog v-model="deleteClassDialog" width="auto" scrim="black">
    <v-card width="40vw" height="" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">刪除主目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">確定要刪除此主目錄嗎？<br />刪除主目錄會將所有屬於該主目錄的技令都刪除掉</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" color="primary_lighter" variant="outlined" size="large" @click="deleteClassDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn color="error" variant="outlined" size="large" @click="async () => {
    await deleteMainClass(deleteMainClassId);
    deleteClassDialog = false;
  }">
          <span> 刪除 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="newClassDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">新增主目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="newClassname" outlined dense clearable class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="addNewMainClass"
          :disabled="newClassname === ''">
          <span> 新增 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editClassDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">編輯主目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="editMainClassData.name" outlined dense clearable
          class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="updateMainClass()">
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
            <div>主目錄編輯頁面</div>
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
          <v-row align="center" v-if="mainClassStore.entryLoading">
            <v-col align="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>
          <v-row align="center" v-for="(item, i) in items" :key="i" style="font-size: 0.8em">
            <v-divider v-if="i !== 0" class="my-2"></v-divider>
            <v-col align="center">
              <v-row align="center">
                <v-col cols="8" align="center">{{ item.name }}</v-col>
                <v-col cols="4">
                  <v-btn icon class="mb-2" color="primary" flat @click="openEditMainClassDialog(item)">
                    <v-icon>mdi-file-document-edit-outline</v-icon>
                  </v-btn>
                  <v-btn icon class="mb-2 ml-3" color="error" flat @click="openDeleteMainClassDialog(item._id)">
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
      <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em" @click="newClassDialog = true">
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
