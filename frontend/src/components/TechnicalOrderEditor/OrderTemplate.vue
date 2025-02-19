<script setup lang="ts">
import { ref, reactive } from "vue";
import { useOrderTemplateColumnStore } from "@store/orderTemplateColumnStore";
import { onMounted } from "vue";

const newColumnName = ref("");
const newColumnType = ref("text");

const newOrderTemplateDialog = ref(false);
const editColumnDialog = ref(false);
const deleteTemplateColumnDialog = ref(false);

const deleteTemplateColumnId = ref("");

const orderTemplateColumnStore = useOrderTemplateColumnStore();

const loading = ref(false);

let editColumnData = reactive({
  _id: "",
  name: "",
});



const updateItems = async () => {
  await orderTemplateColumnStore.init();
};

onMounted(async () => {
  await updateItems();
});

const addNewTemplateColumn = async () => {
  loading.value = true;
  const success = await orderTemplateColumnStore.addItem(
    newColumnName.value,
    newColumnType.value
  );
  loading.value = false;
  if (success) {
    await updateItems();
    newColumnName.value = "";
    newColumnType.value = "text";
    newOrderTemplateDialog.value = false;
  }
};

const typeNameMapping = (type: any) => {
  switch (type) {
    case "text":
      return "文字";
    case "select":
      return "選項";
    case "file-multiple":
      return "多檔案";
    case "select-multiple":
      return "多選項";
    default:
      return "未定義";
  }
};

const openDeleteTemplateColumnDialog = (id: string) => {
  deleteTemplateColumnId.value = id;
  deleteTemplateColumnDialog.value = true;
};

const deleteTemplateColumn = async (id: string) => {
  loading.value = true;
  const success = await orderTemplateColumnStore.deleteItem(id);
  loading.value = false;
  if (success) {
    await updateItems();
  }
};

const openEditColumnDialog = (item: any) => {
  editColumnData._id = item._id;
  editColumnData.name = item.name;
  editColumnDialog.value = true;
};

const updateTemplateColumn = async () => {
  const id = editColumnData._id;
  const name = editColumnData.name;

  loading.value = true;
  const success = await orderTemplateColumnStore.updateItem(id, name);
  loading.value = false;
  if (success) {
    await updateItems();
    editColumnDialog.value = false;
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
  <v-dialog v-model="deleteTemplateColumnDialog" width="auto" scrim="black">
    <v-card width="40vw" height="" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">刪除欄位</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">確定要刪除此欄位嗎？</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" color="primary_lighter" variant="outlined" size="large" @click="deleteTemplateColumnDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn color="error" variant="outlined" size="large" @click="async () => {
          await deleteTemplateColumn(deleteTemplateColumnId);
          deleteTemplateColumnDialog = false;
        }">
          <span> 刪除 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="newOrderTemplateDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">新增文字欄位</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="newColumnName" outlined dense clearable class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="addNewTemplateColumn"
          :disabled="newColumnName === ''">
          <span> 新增 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editColumnDialog" width="auto" scrim="black">
    <v-card width="70vw" height="60vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">編輯欄位名稱</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">名稱</div>
        <v-text-field v-model="editColumnData.name" outlined dense clearable
          class="input-remove-padding"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="updateTemplateColumn">
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
            <div>技令欄位編輯頁面</div>
          </v-col>
        </v-row>
      </v-container>
    </div>
    <v-card-item>
      <v-card color="card_in_card" class="editor-content mb-3">
        <v-container>
          <v-row style="font-size: 0.8em">
            <v-col cols="4" align="center"> 欄位 </v-col>
            <v-col cols="4" align="center"> 類型 </v-col>
            <v-col cols="4" align="center"> 可用操作 </v-col>
            <v-divider class="my-2"></v-divider>
          </v-row>
          <v-row align="center" v-if="orderTemplateColumnStore.entryLoading">
            <v-col align="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>
          <v-row align="center" v-for="(item, i) in orderTemplateColumnStore.getItems" :key="i" style="font-size: 0.8em">
            <v-divider v-if="i !== 0" class="my-2"></v-divider>
            <v-col align="center">
              <v-row align="center">
                <v-col cols="4" align="center">
                  {{ item["name"] }}
                </v-col>
                <v-col cols="4" align="center">
                  {{ typeNameMapping(item["type"]) }}
                </v-col>
                <v-col cols="4">
                  <v-btn icon class="mb-2" color="primary" flat @click="openEditColumnDialog(item)"
                    v-if="item['type'] == 'text' && item['name'] != '步驟名稱' && item['name'] != 'step 步驟'">
                    <v-icon>mdi-file-document-edit-outline</v-icon>
                  </v-btn>
                  <v-btn icon class="mb-2 ml-3" color="error" flat @click="openDeleteTemplateColumnDialog(item['_id'])"
                    v-if="item['type'] == 'text' && item['name'] != '步驟名稱' && item['name'] != 'step 步驟'">
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
      <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em"
        @click="newOrderTemplateDialog = true">
        新增欄位
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
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
</style>
