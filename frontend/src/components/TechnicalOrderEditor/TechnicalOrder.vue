<script setup lang="ts">
import { ref, onMounted, reactive, watch, getCurrentInstance } from "vue";
import { useOrderTemplateColumnStore } from "@store/orderTemplateColumnStore";
import { useMainClassStore } from "@store/mainClassStore";
import { useTechnicalOrderStore } from "../../store/modules/TechnicalOrderStore";
import { useTagStore } from "@store/tagStore";
import { config } from "@/config";
import axios from "axios";
import { authStore } from "@store/authStore";
import MainClass from "./components/TechnicalOrderEditor/MainClass.vue";  // @->.
import InfiniteLoading from "v3-infinite-loading";
import "v3-infinite-loading/lib/style.css";

import { computed } from "vue";
const selectedOriginalMainClassId = computed(() => props.selectedOriginalMainClassId);


const props = defineProps({
  selectedMainClassId: {
    type: String,
    required: true,
    default: "all",
  },
  selectedOriginalMainClassId: {
    type: String,
    required: true,
    default: "all",
  },
  selectedSubClass: {
    type: String,
    required: true,
    default: "全部",
  },
  selectedOptionClass :{
    type: String,
    required: true,
    default: "全部",
  },
  selectedTags: {
    type: Array,
    required: true,
    default: () => [],
  },
});

const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;

watch(
  () => props.selectedMainClassId,
  async (newVal, oldVal) => {
    await initOrderData(newVal, props.selectedSubClass);
  }
);

watch(
  () => selectedOriginalMainClassId.value,
  async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      console.log("🚀 original_id 變更:", newVal);
      await initOrderData(newVal, props.selectedSubClass);
    }
  }
);

watch(
  () => props.selectedSubClass,
  async (newVal, oldVal) => {
    //console.log("監聽結果 ", props.selectedSubClass)
    await initOrderData(props.selectedMainClassId, newVal);
  }
);

watch(
  () => props.selectedOptionClass,
  async (newVal, oldVal) => {
    // console.log("監聽結果 ", props.selectedOptionClass)
    await initOrderData(props.selectedOptionClass, newVal);
  }
);

watch(
  () => props.selectedTags,
  async (newVal, oldVal) => {
    await initOrderData(props.selectedMainClassId, props.selectedSubClass);
  }
);

console.log("✅ TechnicalOrder.vue 收到的 props:", props);

const orderTemplateColumnStore = useOrderTemplateColumnStore();
const technicalOrderStore = useTechnicalOrderStore();
const mainClassStore = useMainClassStore();
const tagStore = useTagStore();

const newTechnicalOrderDialog = ref(false);
const orderTemplateColumns: any = ref<any[]>([]);
const mainClasses: any = ref<any[]>([]);
const subClasses: any = reactive<any[]>([]);
  const optionClasses: any = reactive<any[]>([]);
const newTechnicalOrderData: any = reactive({
  stepName: "",
  stepNumber: "",
  mainClass: "",
  subClass: "",
  optionClass: "",
  tags: [],
  image: null,
  video: null,
  pdf: null,
});
const editTechnicalOrderData: any = reactive({
  _id: "",
  stepName: "",
  stepNumber: "",
  mainClass: "",
  subClass: "",
  optionClass: "",
  tags: [],
  image: null,
  video: null,
  pdf: null,
});
const edit_view_image_file_name_list: any = ref<any[]>([]);
const edit_view_video_file_name_list: any = ref<any[]>([]);
const edit_view_pdf_file_name_list: any = ref<any[]>([]);
const hideEditImageFileName = ref(false);
const hideEditVideoFileName = ref(false);
const hideEditPdfFileName = ref(false);

const updateOptions: any = reactive({
  image: false,
  video: false,
  pdf: false,
});

const newTechnicalOrderForm: any = ref(null);
const editTechnicalOrderForm: any = ref(null);
const orders = ref<any[]>([]);
const filterOrders = ref<any[]>([]);

const editOrderDialog = ref(false);
const updateOptionsDialog = ref(false);
const deleteOrderDialog = ref(false);
const scaledImageDialog = ref(false);

const scaledImageSource = ref("");

const deleteOrderId = ref("");

const loading = ref(false);

const fileSizeLimit = ref(0);
const lastId: any = ref(null);
const stopLoading = ref(false);
const orderFirstItemIdList:any = ref<any[]>([]);
// const tags: any = ref<any[]>([]);

// const updateTagItems = async () => {
//   try {
//     const res = await axios.get(`${config.BACKEND_URL}/technical_orders/tags`, {
//       headers: { Authorization: `Bearer ${authStore().getToken}` },
//     });
//     tags.value = res.data;
//   } catch (error: any) {
//     try {
//       console.log(error.response.status);
//       $toast?.error(error.response.data.detail, {});
//       return false;
//     } catch (error: any) {
//       $toast?.error("後臺發生錯誤，無法取得標籤", {});
//       return false;
//     }
//   }
// };
const initOrderData = async (mainClass: any, subClass: any) => {
  // if (mainClass == "all") {
  //   mainClass = null;
  // }
  // if (subClass == "全部") {
  //   subClass = null;
  // }
  lastId.value = null;
  stopLoading.value = false;
  orders.value.splice(0, orders.value.length);
  orderFirstItemIdList.value.splice(0, orderFirstItemIdList.value.length);
  // const newData = await technicalOrderStore.getItemsWithPaging(null, mainClass, subClass);
  // if (newData.length > 0)
  //   lastId.value = newData[newData.length - 1]._id;
  // orders.value.push(...newData);

  updateFilterOrders();
};

onMounted(async () => {
  await updateFileSizeLimit();
  await orderTemplateColumnStore.init();
  orderTemplateColumns.value = orderTemplateColumnStore.getItems;

  // orders.value = 
  // technicalOrderStore.getItemsWithPaging(null);
  // clear any push data arry into orders
  // await initOrderData(props.selectedMainClassId, props.selectedSubClass);

  // sort by mainClass and subClass, then stepNumber
  // orders.value.sort((a: any, b: any) => {
  //   if (a.mainClass > b.mainClass) return 1;
  //   if (a.mainClass < b.mainClass) return -1;
  //   if (a.subClass > b.subClass) return 1;
  //   if (a.subClass < b.subClass) return -1;
  //   if (a.stepNumber > b.stepNumber) return 1;
  //   if (a.stepNumber < b.stepNumber) return -1;
  //   return 0;
  // });

  const sortOrder = [
    "步驟名稱",
    "step 步驟",
    "主目錄",
    "次目錄",
    "選項",
    "標籤",
    "輔助圖片",
    "輔助影片",
    "輔助 PDF",
  ];
  console.log("🔍 orderTemplateColumns:", orderTemplateColumns);

  orderTemplateColumns.value.sort((a: any, b: any) => {
    let indexA = sortOrder.indexOf(a.name);
    let indexB = sortOrder.indexOf(b.name);

    if (indexA === -1) indexA = sortOrder.length;
    if (indexB === -1) indexB = sortOrder.length;

    return indexA - indexB;
  });

  // await updateTagItems();
  await mainClassStore.init();
  mainClasses.value = mainClassStore.getItems;
});

const updateFileSizeLimit = async () => {
  fileSizeLimit.value = 0;
  try {
    const res = await axios.get(`${config.BACKEND_URL}/technical_orders/orders/file_size_limit`, {
    });
    fileSizeLimit.value = res.data.file_size_limit;
  } catch (error: any) {
    console.log(error);
  }
};

const renderMoreData = async ($state: any) => {
  console.log("renderMoreData");
  let mainClass:any = props.selectedMainClassId;
  let subClass:any = props.selectedSubClass;
  let optionClass:any = props.selectedOptionClass;
  let originalMainClass:any = props.selectedOriginalMainClassId;
 
  if (originalMainClass == "all") {
    originalMainClass = null;
  }
  if (mainClass == "all") {
    mainClass = null;
  }
  if (mainClass == "all") {
    mainClass = null;
  }
  if (originalMainClass == "全部") {
    originalMainClass = null;
  }
  if (optionClass == "全部") {
    optionClass = null;
  }

  if (stopLoading.value) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    $state.loaded();
    return;
  }
  console.log("原始mainClass的ID : ", mainClass)
  console.log("現有mainClass的ID : ", originalMainClass)
  console.log("原始subClass: ", subClass)
  const newData = await technicalOrderStore.getItemsWithPaging(lastId.value, mainClass, subClass, optionClass, originalMainClass);
  if (newData.length > 0 && orderFirstItemIdList.value.findIndex((itemId:any) => itemId === newData[0]._id) !== -1) {
    $state.loaded();
    return;
  }
  if (newData.length > 0){ 
    orderFirstItemIdList.value.push(newData[0]._id);
    lastId.value = newData[newData.length - 1]._id;
    orders.value.push(...newData);
  }
  else if (newData.length === 0) {
    stopLoading.value = true;
    $state.loaded();
    return;
  }
  updateFilterOrders();
  await new Promise((resolve) => setTimeout(resolve, 1));

  $state.loaded();
};

const filterOrdersByTags = (tags: any[]) => {
  if (tags.length === 0) {
    return;
  }

  filterOrders.value = filterOrders.value.filter((order) => {
    for (let tag of tags) {
      // check if order have attribute tag
      if (!order.tags) {
        return false;
      }
      if (!order.tags.includes(tag)) {
        return false;
      }
    }
    return true;
  });
}

const updateFilterOrders = () => {
  filterOrders.value = orders.value;
  filterOrdersByTags(props.selectedTags);
}


const addNewTechnicalOrder = async () => { 
  if (!((await newTechnicalOrderForm.value.validate()).valid)) {
    $toast?.error("表單有欄位驗證沒過", {});
    return;
  }

  try {
    loading.value = true;
    const selectedMainClass = mainClassStore.items.find(
    (item) => item._id === newTechnicalOrderData.mainClass
  );
  if (selectedMainClass?.original_id) {
    newTechnicalOrderData.mainClass = selectedMainClass.original_id;
  }

    await technicalOrderStore.addItem(newTechnicalOrderData);
    await initOrderData(props.selectedMainClassId, props.selectedSubClass);

    // iterate every key and set to ""
    console.log("Answer", props.selectedOriginalMainClassId);
    console.log("SubClass", props.selectedSubClass);
    console.log("optionClass 是啥", props.selectedOptionClass);
    for (let key in newTechnicalOrderData) {
      newTechnicalOrderData[key] = "";
    }

    newTechnicalOrderDialog.value = false;
    // clear newTechnicalOrderData
    newTechnicalOrderData.image = null;
    newTechnicalOrderData.video = null;
    newTechnicalOrderData.pdf = null;
    newTechnicalOrderData.tags = [];

    await initOrderData(props.selectedOriginalMainClassId, props.selectedSubClass);
    console.log(orders.value);

    console.log("addNewTechnicalOrder");
  }
  catch (error: any) {

  }
  loading.value = false;

};

const getFirstImageUrl = (imageIdList: any[]) => {
  if (imageIdList.length === 0) return "";

  return `${config.BACKEND_URL}/technical_orders/orders/image_file/${imageIdList[0]}`;
};

const deleteOrder = async (orderId: string) => {
  loading.value = true;
  await technicalOrderStore.deleteItem(orderId);
  await initOrderData(props.selectedMainClassId, props.selectedSubClass);
  loading.value = false;
};

const openDeleteOrderDialog = (orderId: string) => {
  deleteOrderId.value = orderId;
  deleteOrderDialog.value = true;
};

const openEditOrderDialog = async (order: any) => {
  console.log(order);
  order.image = null;
  order.video = null;
  order.pdf = null;
  Object.assign(editTechnicalOrderData, order);
  await mainClassStore.selectEditMainClass(editTechnicalOrderData.mainClass);

  edit_view_image_file_name_list.value = [];
  for (let image_id of order.image_id_list) {
    const image_file_name = await get_image_file_name_by_id(image_id);
    edit_view_image_file_name_list.value.push(image_file_name);
  }

  edit_view_video_file_name_list.value = [];
  for (let video_id of order.video_id_list) {
    const video_file_name = await get_image_file_name_by_id(video_id);
    edit_view_video_file_name_list.value.push(video_file_name);
  }

  edit_view_pdf_file_name_list.value = [];
  for (let pdf_id of order.pdf_id_list) {
    const pdf_file_name = await get_image_file_name_by_id(pdf_id);
    edit_view_pdf_file_name_list.value.push(pdf_file_name);
  }

  editOrderDialog.value = true;
};

const duplicateOrder = async (orderId: string) => {
  loading.value = true;
  try {
    const response = await axios.post(
      `${config.BACKEND_URL}/technical_orders/orders/duplicate/${orderId}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      },
    );
    await initOrderData(props.selectedMainClassId, props.selectedSubClass);
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法複製技令", {});
    }
  }
  loading.value = false;
};

const get_image_file_url = (file_id: string) => {
  return `${config.BACKEND_URL}/technical_orders/orders/image_file/${file_id}`;
};

const get_image_file_name_by_id = async (file_id: string) => {
  try {
    const response = await axios.get(
      `${config.BACKEND_URL}/technical_orders/orders/file/${file_id}`,
      {
        headers: {
          Authorization: `Bearer ${authStore().getToken}`,
        },
      }
    );
    return response.data["file_name"];
  } catch (error: any) {
    try {
      console.log(error.response.status);
      $toast?.error(error.response.data.detail, {});
    }
    catch (error: any) {
      $toast?.error("後臺發生錯誤，無法取得檔案名稱", {});
    }
  }
};

const get_video_file_url = (file_id: string) => {
  return `${config.BACKEND_URL}/technical_orders/orders/video_file/${file_id}`;
};

const get_pdf_file_url = (file_id: string) => {
  return `${config.BACKEND_URL}/technical_orders/orders/pdf_file/${file_id}`;
};

const updateEditOrderData = async () => {
  if (!((await editTechnicalOrderForm.value.validate()).valid)) {
    $toast?.error("表單有欄位驗證沒過", {});
    return;
  }
  try {
    loading.value = true;

    let sendData: any = {}
    let file_success = true;

    Object.assign(sendData, editTechnicalOrderData);
    const sendDataId = sendData._id;
    console.log("sendDataId", sendDataId);

    console.log("editTechnicalOrderData.image", editTechnicalOrderData.image);
    delete sendData.image;
    delete sendData.video;
    delete sendData.pdf;

    delete sendData.value;
    delete sendData._id;

    const successFlag = await technicalOrderStore.updateItem(sendDataId, sendData, false);

    if (!successFlag) {
      return;
    }

    if (updateOptions.image) {
      Object.assign(sendData, editTechnicalOrderData);
      let formData = new FormData();
      console.log("sendData.image", sendData.image);
      if (Array.isArray(sendData.image)) {
        sendData.image.forEach((file: any, index: any) => {
          formData.append(`image[${index}]`, file);
        });
      } else {
        formData.append(`image[0]`, "null");
      }

      try {
        const response = await axios.put(
          `${config.BACKEND_URL}/technical_orders/orders/${sendDataId}/images`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        $toast?.success("圖片更新成功", {});
      } catch (error: any) {
        try {
          file_success = false;
          console.log(error.response.status);
          $toast?.error(error.response.data.detail, {});
        }
        catch (error: any) {
          $toast?.error("後臺發生錯誤，無法更新圖片", {});
        }
      }
    }

    if (updateOptions.video) {
      Object.assign(sendData, editTechnicalOrderData);
      let formData = new FormData();
      console.log("sendData.video", sendData.video);
      if (Array.isArray(sendData.video)) {
        sendData.video.forEach((file: any, index: any) => {
          formData.append(`video[${index}]`, file);
        });
      } else {
        formData.append(`video[0]`, "null");
      }

      try {
        const response = await axios.put(
          `${config.BACKEND_URL}/technical_orders/orders/${sendDataId}/videos`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        $toast?.success("影片欄位更新成功", {});
      } catch (error: any) {
        try {
          file_success = false;
          console.log(error.response.status);
          $toast?.error(error.response.data.detail, {});
        }
        catch (error: any) {
          $toast?.error("後臺發生錯誤，無法更新影片", {});
        }
      }
    }

    if (updateOptions.pdf) {
      Object.assign(sendData, editTechnicalOrderData);
      let formData = new FormData();
      console.log("sendData.pdf", sendData.pdf);
      if (Array.isArray(sendData.pdf)) {
        sendData.pdf.forEach((file: any, index: any) => {
          formData.append(`pdf[${index}]`, file);
        });
      } else {
        formData.append(`pdf[0]`, "null");
      }

      try {
        const response = await axios.put(
          `${config.BACKEND_URL}/technical_orders/orders/${sendDataId}/pdfs`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        $toast?.success("PDF 更新成功", {});
      } catch (error: any) {
        try {
          file_success = false;
          console.log(error.response.status);
          $toast?.error(error.response.data.detail, {});
        } catch (error: any) {
          $toast?.error("後臺發生錯誤，無法更新 PDF", {});
        }
      }
    }


    await initOrderData(props.selectedMainClassId, props.selectedSubClass);
    if (file_success) {
      $toast?.success("更新成功", {});
    }
    else {
      $toast?.error("除了檔案的部分，其餘部分皆有更新", {});
    }

    editTechnicalOrderData.value = {
      _id: "",
      stepName: "",
      stepNumber: "",
      mainClass: "",
      subClass: "",
      image: null,
      video: null,
      pdf: null,
    };

    Object.assign(updateOptions, {
      image: false,
      video: false,
      pdf: false,
    });

    updateOptionsDialog.value = false;
    editOrderDialog.value = false;
  }
  catch (error: any) {
  }
  loading.value = false;
};
</script>

<template>
  <v-dialog v-model="scaledImageDialog" width="auto" scrim="black">
    <v-card width="80vw" max-height="80vh" class="pa-6">
      <v-card-text>
        <v-img :src="scaledImageSource" />
      </v-card-text>
    </v-card>
  </v-dialog>

  <v-dialog v-model="deleteOrderDialog" width="auto" scrim="black">
    <v-card width="40vw" height="" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">刪除技令</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em">確定要刪除此技令嗎？</div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" color="primary_lighter" variant="outlined" size="large" @click="deleteOrderDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn color="error" variant="outlined" size="large" @click="async () => {
          await deleteOrder(deleteOrderId);
          deleteOrderDialog = false;
        }">
          <span> 刪除 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

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

  <v-dialog v-model="updateOptionsDialog" width="auto" scrim="black">
    <v-card width="70vw" height="80vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">更新選項</div>
      </v-card-title>
      <v-card-text>
        <div style="font-size: 1.2em" class="mb-10">勾選想要更新的檔案選項，若是勾選，會清除原有的勾選類別檔案，並且根據您選擇的檔案重新更新</div>


        <v-card color="card_in_card" class="pa-5 mb-5" flat>
          <v-container>
            <v-row align="center">
              <v-flex xs5>
                <v-layout>
                  <v-checkbox v-model="updateOptions.image" label="" color="primary" class="ma-0 pa-0 mr-2"
                    hide-details></v-checkbox>

                </v-layout>
              </v-flex>
              <span>更新圖片</span>
            </v-row>

            <v-row align="center">
              <v-flex xs5>
                <v-layout>
                  <v-checkbox v-model="updateOptions.video" label="" color="primary" class="ma-0 pa-0 mr-2"
                    hide-details></v-checkbox>

                </v-layout>
              </v-flex>
              <span>更新影片</span>
            </v-row>
            <v-row align="center">
              <v-flex xs5>
                <v-layout>
                  <v-checkbox v-model="updateOptions.pdf" label="" color="primary" class="ma-0 pa-0 mr-2"
                    hide-details></v-checkbox>

                </v-layout>
              </v-flex>
              <span>更新 PDF</span>
            </v-row>
          </v-container>
        </v-card>

      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="outlined" size="large" @click="updateOptionsDialog = false">
          <span> 取消 </span>
        </v-btn>
        <v-btn class="ml-7" color="primary_lighter" variant="outlined" size="large" @click="updateEditOrderData()">
          <span> 更新 </span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="editOrderDialog" width="auto" scrim="black">
    <v-card width="70vw" height="80vh" class="pa-6">
      <v-card-title>
        <div style="font-size: 1.6em">更新技令</div>
      </v-card-title>
      <v-card-text>
        <v-form ref="editTechnicalOrderForm" @submit.prevent>
          <div class="mb-5 mb-2">
            <div style="font-size: 1.2em">當前圖片</div>
            <v-carousel v-if="editTechnicalOrderData.image_id_list.length > 0" hide-delimiters>
              <template v-slot:prev="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-left"></v-btn>
              </template>

              <template v-slot:next="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-right"></v-btn>
              </template>
              <v-carousel-item v-for="(image, i) in editTechnicalOrderData.image_id_list" :key="i">
                <div>
                  <v-img :src="get_image_file_url(image)" class="edit-video" @click="() => {
                    scaledImageSource = get_image_file_url(image);
                    scaledImageDialog = true;
                  }" style="cursor: pointer;background-color: #000000" @mouseover="hideEditImageFileName = true"
                    @mouseleave="hideEditImageFileName = false" />
                  />
                  <div :class="{ 'hidden': hideEditImageFileName }"
                    style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.5); color: white; text-align: center; font-size: 0.9em;">
                    {{ edit_view_image_file_name_list[i] }}
                  </div>
                </div>
              </v-carousel-item>
            </v-carousel>
            <div v-else>無圖片</div>

            <div class="mt-5 mb-2" style="font-size: 1.2em">當前影片</div>
            <v-carousel v-if="editTechnicalOrderData.video_id_list.length > 0" hide-delimiters>

              <template v-slot:prev="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-left"></v-btn>
              </template>

              <template v-slot:next="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-right"></v-btn>
              </template>
              <v-carousel-item v-for="(video, i) in editTechnicalOrderData.video_id_list" :key="i">
                <div class="d-flex fill-height justify-center align-center">
                  <!-- <video-player v-if="editOrderDialog" :src="async ()=>{await get_video_file_url(video)}" :controls="true" :loop="true"
                    :volume="0.6" style="width: 100%; z-index: 100;"></video-player> -->
                  <div class="edit-video-container">
                    <iframe class="edit-video" :src="get_video_file_url(video)" allowfullscreen
                      @mouseover="hideEditVideoFileName = true" @mouseleave="hideEditVideoFileName = false" />
                    <div :class="{ 'hidden': hideEditVideoFileName }"
                      style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.5); color: white; text-align: center; font-size: 0.9em;">
                      {{ edit_view_video_file_name_list[i] }}
                    </div>
                  </div>
                </div>
              </v-carousel-item>
            </v-carousel>
            <div v-else>無影片</div>
            <div class="mt-5 mb-2" style="font-size: 1.2em">當前 PDF</div>
            <v-carousel v-if="editTechnicalOrderData.pdf_id_list.length > 0" hide-delimiters>

              <template v-slot:prev="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-left"></v-btn>
              </template>

              <template v-slot:next="{ props }">
                <v-btn color="primary" @click="props.onClick" icon="mdi-chevron-right"></v-btn>
              </template>
              <v-carousel-item v-for="(pdf, i) in editTechnicalOrderData.pdf_id_list" :key="i">

                <embed class="edit-video" :src="get_pdf_file_url(pdf)" type="application/pdf" height="600px"
                  @mouseover="hideEditPdfFileName = true" @mouseleave="hideEditPdfFileName = false" />
                <div :class="{ 'hidden': hideEditPdfFileName }"
                  style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.5); color: white; text-align: center; font-size: 0.9em;">
                  {{ edit_view_pdf_file_name_list[i] }}
                </div>
              </v-carousel-item>
            </v-carousel>
            <div v-else>無 PDF</div>
          </div>
          <div v-for="templateColumn in orderTemplateColumns" :key="templateColumn._id">
            <div style="font-size: 1.2em">{{ templateColumn.name }}</div>
            <v-text-field v-if="templateColumn.type === 'text' &&
              templateColumn.name === '步驟名稱'
            " v-model="editTechnicalOrderData.stepName" :rules="[(v: any) => !!v || '必須填寫步驟名稱']" variant="outlined"
              dense></v-text-field>
            <v-text-field v-else-if="templateColumn.type === 'text' &&
              templateColumn.name === 'step 步驟'
            " v-model="editTechnicalOrderData.stepNumber" :rules="[(v: any) => !!v || '必須填寫步驟']" variant="outlined"
              dense></v-text-field>
            <v-textarea v-else-if="templateColumn.type === 'text'" v-model="editTechnicalOrderData[templateColumn.name]"
              variant="outlined" rows="1" :auto-grow="true" row-height="15"></v-textarea>
            <v-select v-else-if="templateColumn.type === 'select' &&
              templateColumn.name === '主目錄'
            " :rules="[(v: any) => !!v || '必須填寫主目錄']" v-model="editTechnicalOrderData.mainClass" variant="outlined"
              dense :items="mainClasses" item-title="name" item-value="_id" @update:model-value="async () => {
                editTechnicalOrderData.subClass = '';
                // await mainClassStore.selectMainClass(
                //   editTechnicalOrderData.mainClass
                // );
                await mainClassStore.selectEditMainClass(
                  editTechnicalOrderData.mainClass
                );

                // Object.assign(subClasses, mainClassStore.getSubClasses);

                // if (mainClassStore.getSubClasses.length === 0)
                //   subClasses.splice(0, subClasses.length);
              }
                "></v-select>
            <v-select v-else-if="templateColumn.type === 'select' &&
              templateColumn.name === '次目錄'
            " :rules="[(v: any) => !!v || '必須填寫次目錄']" v-model="editTechnicalOrderData.subClass" variant="outlined"
              dense :items="mainClassStore.editSubClasses" item-title="sub_class" item-value="sub_class"></v-select>
            <v-select v-else-if="templateColumn.type === 'select-multiple' &&
              templateColumn.name === '標籤'
            " clearable v-model="editTechnicalOrderData.tags" multiple :items="tagStore.tags" item-title="name"
              item-value="_id" variant="outlined" chips dense />
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name === '輔助圖片'
            " multiple v-model="editTechnicalOrderData.image" accept=".png, .jpg .jpeg" variant="outlined"
            :rules="[(v: any) => {
              if (v) {
                for (let file of v) {
                  if (file.size > fileSizeLimit) {
                    return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                  }
                }
                return true;
              }
              return true;
            }]" dense></v-file-input>
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name === '輔助影片'
            " multiple v-model="editTechnicalOrderData.video" accept="video/mp4" variant="outlined"
            :rules="[(v: any) => {
              if (v) {
                for (let file of v) {
                  if (file.size > fileSizeLimit) {
                    return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                  }
                }
                return true;
              }
              return true;
            }]" dense></v-file-input>
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name == '輔助 PDF'
            " multiple v-model="editTechnicalOrderData.pdf" accept="application/pdf" variant="outlined"
            :rules="[(v: any) => {
              if (v) {
                for (let file of v) {
                  if (file.size > fileSizeLimit) {
                    return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                  }
                }
                return true;
              }
              return true;
            }]" dense></v-file-input>
          </div>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary_lighter" variant="outlined" size="large" @click="updateOptionsDialog = true">
          <span> 更新</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="newTechnicalOrderDialog" width="auto" scrim="black">
    <v-form ref="newTechnicalOrderForm" @submit.prevent>
      <v-card width="70vw" height="60vh" class="pa-6">
        <v-card-title>
          <div style="font-size: 1.6em">新增技令</div>
        </v-card-title>
        <v-card-text>

          <div v-for="templateColumn in orderTemplateColumns" :key="templateColumn._id">
            <div style="font-size: 1.2em">{{ templateColumn.name }}</div>
            <v-text-field v-if="templateColumn.type === 'text' &&
              templateColumn.name === '步驟名稱'
            " v-model="newTechnicalOrderData.stepName" :rules="[(v: any) => !!v || '必須填寫步驟名稱']" variant="outlined"
              dense></v-text-field>
            <v-text-field v-else-if="templateColumn.type === 'text' &&
              templateColumn.name === 'step 步驟'
            " v-model="newTechnicalOrderData.stepNumber" :rules="[(v: any) => !!v || '必須填寫步驟']" variant="outlined"
              dense></v-text-field>
            <v-textarea v-else-if="templateColumn.type === 'text'" v-model="newTechnicalOrderData[templateColumn.name]"
              variant="outlined" rows="1" :auto-grow="true" row-height="15"></v-textarea>
            <v-select v-else-if="templateColumn.type === 'select' &&
              templateColumn.name === '主目錄'
            " :rules="[(v: any) => !!v || '必須填寫主目錄']" v-model="newTechnicalOrderData.mainClass" variant="outlined"
              dense :items="mainClasses" item-title="name" item-value="_id" @update:model-value="async () => {
                newTechnicalOrderData.subClass = '';
                await mainClassStore.selectMainClass(
                  newTechnicalOrderData.mainClass
                );

                Object.assign(subClasses, mainClassStore.getSubClasses);

                if (mainClassStore.getSubClasses.length === 0)
                  subClasses.splice(0, subClasses.length);
              }
                "></v-select>
              <v-select v-else-if="templateColumn.type === 'select' &&
                templateColumn.name === '次目錄'"
                :rules="[(v: any) => !!v || '必須填寫次目錄']"
                v-model="newTechnicalOrderData.subClass"
                variant="outlined"
                dense
                :items="subClasses"
                item-title="sub_class"
                item-value="sub_class"
                @update:model-value="async () => {
                  newTechnicalOrderData.optionClass = '';

                  await mainClassStore.selectSubClass(newTechnicalOrderData.mainClass, newTechnicalOrderData.subClass);

                  // 更新 optionClasses
                  Object.assign(optionClasses, mainClassStore.getOptionClasses);

                  if (mainClassStore.getOptionClasses.length === 0)
                    optionClasses.splice(0, optionClasses.length);
                }"
              />

              <v-select
                v-else-if="templateColumn.type === 'select' && templateColumn.name === '選項'"
                :rules="[(v: any) => !!v || '必須填寫選項']"
                v-model="newTechnicalOrderData.optionClass"
                variant="outlined"
                dense
                :items="Array.isArray(optionClasses) 
                  ? optionClasses.filter(item => item?.option_class && item.option_class !== '全部') 
                  : []"
                item-title="option_class"
                item-value="option_class"
                @update:model-value="(val) => {
                  // ✅ 記錄使用者選的選項
                  mainClassStore.selectedOptionClass.option_class = val;
                }"
              />
            <v-select v-else-if="templateColumn.type === 'select-multiple' &&
              templateColumn.name === '標籤'
            " clearable item-title="name" item-value="_id" v-model="newTechnicalOrderData.tags" multiple
              :items="tagStore.tags" variant="outlined" chips dense />
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name === '輔助圖片'
            " multiple v-model="newTechnicalOrderData.image" accept="image/png, image/jpeg" variant="outlined"
              :rules="[(v: any) => {
                if (v) {
                  for (let file of v) {
                    if (file.size > fileSizeLimit) {
                      return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                    }
                  }
                  return true;
                }
                return true;
              }]"
              dense></v-file-input>
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name === '輔助影片'
            " multiple v-model="newTechnicalOrderData.video" accept="video/mp4" variant="outlined"
              :rules="[(v: any) => {
                if (v) {
                  for (let file of v) {
                    if (file.size > fileSizeLimit) {
                      return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                    }
                  }
                  return true;
                }
                return true;
              }]"
              dense></v-file-input>
            <v-file-input v-else-if="templateColumn.type === 'file-multiple' &&
              templateColumn.name === '輔助 PDF'
            " multiple v-model="newTechnicalOrderData.pdf" accept="application/pdf" variant="outlined"
              :rules="[(v: any) => {
                if (v) {
                  for (let file of v) {
                    if (file.size > fileSizeLimit) {
                      return '單一檔案大小超過限制: ' + fileSizeLimit / 1024 / 1024 + ' MB';
                    }
                  }
                  return true;
                }
                return true;
              }]"
              dense></v-file-input>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn type="submit" color="primary_lighter" variant="outlined" size="large" @click="addNewTechnicalOrder">
            <span> 新增 </span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
  <v-card class="main-content pa-5 pt-2" flat>
    <div class="py-0 pt-0">
      <v-container>
        <v-row>
          <v-col>
            <div>技令編輯頁面</div>
          </v-col>
        </v-row>
      </v-container>
    </div>
    <v-card-item>
      <v-card color="card_in_card" class="editor-content mb-3">
        <v-container>
          <v-row style="font-size: 0.8em">
            <v-col cols="2" align="center"> 預覽照片 </v-col>
            <v-col cols="2" align="center"> 步驟 </v-col>
            <v-col cols="5" align="center"> 步驟名稱 </v-col>
            <v-col cols="3" align="center"> 可用操作 </v-col>
          </v-row>
          <v-divider class="my-2 mb-5"></v-divider>
          <v-row align="center" v-for="(order, i) in filterOrders" :key="i" style="font-size: 0.8em">
            <div style="width: 100%">
              <v-divider v-if="i !== 0" class="my-2"></v-divider>
              <v-col align="center">
                <v-row align="center">
                  <v-col cols="2" align="center">
                    <v-img :width="50" :aspect-ratio="1" cover :src="getFirstImageUrl(order['image_id_list'])" />
                  </v-col>
                  <v-col cols="2" align="center">{{ order["stepNumber"] }}</v-col>
                  <v-col cols="5" align="center">
                    <!-- <div class="text-truncate"> -->
                    <div class="">
                      {{ order["stepName"] }}
                    </div>
                  </v-col>
                  <v-col cols="3">
                    <v-btn icon class="mb-2" color="secondary" flat @click="duplicateOrder(order._id)">
                      <v-icon>mdi-content-copy</v-icon>
                    </v-btn>
                    <v-btn icon class="mb-2 ml-3" color="primary" flat
                      @click="async () => { await openEditOrderDialog(order) }">
                      <v-icon>mdi-file-document-edit-outline</v-icon>
                    </v-btn>
                    <v-btn icon class="mb-2 ml-3" color="error" flat @click="openDeleteOrderDialog(order._id)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-col>
            </div>
          </v-row>
          <v-row align="center" v-if="technicalOrderStore.entryLoading">
            <v-col align="center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col align="center">
              <infinite-loading @infinite="renderMoreData">
                <template #spinner>
                  <span></span>
                </template>
                <template #complete>
                  <span></span>
                </template>

              </infinite-loading>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </v-card-item>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" variant="flat" size="large" style="font-size: 0.75em"
        @click="newTechnicalOrderDialog = true">
        新增
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.hidden {
  display: none;
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

.edit-video-container {
  /* width: 100%; */
  /* max-width: 100%; */
  /* height: 100vh; */
  /* max-height: 100vh; */
  /* object-fit: contain; */
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 40%;
}

.edit-video {
  /* width: 100%; */
  /* max-width: 100%; */
  /* height: 100%; */
  /* max-height: 100vh; */
  /* object-fit: contain; */

  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
