<script setup lang="ts">
import { ref, reactive } from "vue";
import { useMainClassStore } from "@store/mainClassStore";
import { onMounted } from "vue";

const items: any = ref<any[]>([]);

const newMainClassName = ref("");
const newClassname = ref("");

const newClassDialog = ref(false);
const editClassDialog = ref(false);
const deleteClassDialog = ref(false);

const deleteMainClassId = ref("");
const deleteSubClassName = ref("");

const loading = ref(false);

let editSubClassData = reactive({
  _id: "",
  mainClass: "",
  subClass: "",
});
const originalSubClassName = ref("");

const mainClassStore = useMainClassStore();
// mount
onMounted(async () => {
  await mainClassStore.init();
  await mainClassStore.selectMainClass(mainClassStore.selectedMainClass._id);
  items.value = mainClassStore.getSubClasses;
});

const openNewSubClassDialog = () => {
  newMainClassName.value = mainClassStore.selectedMainClass._id;
  if (newMainClassName.value === "all") {
    newMainClassName.value = "";
  }
  newClassDialog.value = true;
};

const openEditSubClassDialog = (item: any) => {
  editSubClassData._id = item.main_class_id;
  editSubClassData.mainClass = item.main_class;
  editSubClassData.subClass = item.sub_class;
  originalSubClassName.value = item.sub_class;

  editClassDialog.value = true;
};

const addNewSubClass = async () => {
  loading.value = true;
  const success = await mainClassStore.addSubClass(
    newMainClassName.value,
    newClassname.value
  );
  loading.value = false;
  if (success) {
    mainClassStore.updateSubClasses(mainClassStore.selectedMainClass._id);
    newMainClassName.value = "";
    newClassname.value = "";
    newClassDialog.value = false;
  }
};

const updateSubClass = async () => {
  const id = editSubClassData._id;
  const newName = editSubClassData.subClass;
  loading.value = true;
  const success = await mainClassStore.patchSubClass(
    id,
    originalSubClassName.value,
    newName
  );
  loading.value = false;
  if (success) {
    items.value = mainClassStore.updateSubClasses(
      mainClassStore.selectedMainClass._id
    );
    editClassDialog.value = false;
  }
};

const openDeleteSubClassDialog = (mainClassId: string, subClassName: string) => {
  deleteClassDialog.value = true;
  deleteMainClassId.value = mainClassId;
  deleteSubClassName.value = subClassName;
};

const deleteSubClass = async (mainClassId: string, subClassName: string) => {
  loading.value = true;
  const success = await mainClassStore.deleteSubClass(
    mainClassId,
    subClassName
  );
  loading.value = false;
  if (success) {
    items.value = mainClassStore.getItems;
  }
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
        <div style="font-size: 1.6em">刪除次目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">確定要刪除此次目錄嗎？<br />刪除次目錄會將所有屬於該次目錄的技令都刪除掉</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" color="primary_lighter" variant="outlined" size="large" @click="deleteClassDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn color="error" variant="outlined" size="large" @click="async () => {
    await deleteSubClass(deleteMainClassId, deleteSubClassName);
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
        <div style="font-size: 1.6em">新增次目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">主目錄</div>
        <v-select :items="mainClassStore.getItems" item-title="name" item-value="_id" outlined dense
          class="input-remove-padding" v-model="newMainClassName" />
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="newClassname" outlined dense clearable class="input-remove-padding">
        </v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="addNewSubClass"
          :disabled="newClassname === '' || newMainClassName === ''">
          <span> 新增 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editClassDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">編輯次目錄</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">所屬主目錄</div>
        <v-text-field v-model="editSubClassData.mainClass" outlined dense class="input-remove-padding"
          :readonly="true"></v-text-field>
        <div style="font-size: 1.2em">次目錄名稱</div>
        <v-text-field v-model="editSubClassData.subClass" outlined dense clearable
          class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="updateSubClass"
          :disabled="editSubClassData.subClass === originalSubClassName">
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
            <div>次目錄編輯頁面</div>
          </v-col>
        </v-row>
      </v-container>
    </div>
    <v-card-item>
      <v-card color="card_in_card" class="editor-content mb-3">
        <v-container>
          <v-row style="font-size: 0.8em">
            <v-col cols="4" align="center"> 主目錄 </v-col>
            <v-col cols="4" align="center"> 名稱 </v-col>
            <v-col cols="4" align="center"> 可用操作 </v-col>
            <v-divider class="my-2 mb-5"></v-divider>
          </v-row>
          <v-row align="center" v-if="mainClassStore.subClassEntryLoading">
            <v-col align="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>
          <v-row align="center" v-for="(item, i) in mainClassStore.getSubClasses" :key="i" style="font-size: 0.8em">
            <v-divider v-if="!(
    i == 0 ||
    (i == 1 &&
      mainClassStore.getSubClasses.length > 0 &&
      mainClassStore.getSubClasses[0].main_class == 'all')
  )
    " class="my-2"></v-divider>
            <v-col align="center" v-if="item.main_class != 'all'">
              <v-row align="center">
                <v-col cols="4" align="center">{{ item.main_class }}</v-col>
                <v-col cols="4" align="center">{{ item.sub_class }}</v-col>
                <v-col cols="4">
                  <v-btn icon class="mb-2" color="primary" flat @click="openEditSubClassDialog(item)">
                    <v-icon>mdi-file-document-edit-outline</v-icon>
                  </v-btn>
                  <v-btn icon class="mb-2 ml-3" color="error" flat
                    @click="openDeleteSubClassDialog(item.main_class_id, item.sub_class)">
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
      <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em" @click="openNewSubClassDialog">
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
