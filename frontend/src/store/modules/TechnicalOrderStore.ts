import { defineStore } from "pinia";
import axios from "axios";
import { authStore } from "@store/authStore";
import { config } from "@/config";
import { getCurrentInstance } from "vue";

export const useTechnicalOrderStore = defineStore("technicalOrderStore", {
  state: () => ({
    mainClass: "" as String,
    originalId: "" as string,
    subClass: "" as String,
    optionClass: "" as string,
    $toast: getCurrentInstance()?.appContext.config.globalProperties.$toast,
    entryLoading: false,
  }),
  actions: {
    
    async getItemsWithPaging(lastId: any, mainClass: any, subClass: any, optionClass: any, originalId: any) {
      const items = []
      try {
        this.entryLoading = true;
        // get items from backend
        const queryParams :any = {
          timestamp: new Date().getTime(),
          page_mode: "true",
        }
        if (lastId != null) {
          queryParams["last_id"] = lastId;
        }
        if (originalId != null){
          queryParams["original_id"] = originalId;
        }
        if (mainClass != null) {
          queryParams["main_class"] = mainClass;
        }
        if (subClass != null) {
          queryParams["sub_class"] = subClass;
        }
        if (optionClass != null){
          queryParams["option_class"] = optionClass;
        }
        console.log("original_id 在這裡 : ",originalId)
        const response = await axios.get(
          `${config.BACKEND_URL}/technical_orders/orders/new/order`,
          {
            params: queryParams,
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        this.entryLoading = false;
        return response.data;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法取得技令", {});
        }
      }
      this.entryLoading = false;
      return []
    },
    

    async addItem(newOrderData: any) {
      let formData = new FormData();

      // 添加一般字段
      Object.keys(newOrderData).forEach((key) => {
        if (key !== "image" && key !== "video" && key !== "pdf") {
          formData.append(key, newOrderData[key]);
        }
      });

      // 處理 image 和 video，確保它們是列表
      if (Array.isArray(newOrderData.image)) {
        newOrderData.image.forEach((file: any, index: any) => {
          formData.append(`image[${index}]`, file);
        });
      }

      if (Array.isArray(newOrderData.video)) {
        newOrderData.video.forEach((file: any, index: any) => {
          formData.append(`video[${index}]`, file);
        });
      }

      if (Array.isArray(newOrderData.pdf)) {
        newOrderData.pdf.forEach((file: any, index: any) => {
          formData.append(`pdf[${index}]`, file);
        });
      }

      // tags
      if (Array.isArray(newOrderData.tags)) {
        newOrderData.tags.forEach((tag: any, index: any) => {
          formData.append(`tag[${index}]`, tag);
        });
      }

      try {
        const response = await axios.post(
          `${config.BACKEND_URL}/technical_orders/orders`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        this.$toast?.success("成功添加技令");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法添加技令", {});
        }
      }
    },
    async deleteItem(id: string) {
      try {
        const response = await axios.delete(
          `${config.BACKEND_URL}/technical_orders/orders/${id}`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        this.$toast?.success("刪除成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法刪除技令", {});
        }
      }
    },
    async updateItem(id: any, sendData: any, withFile: boolean) {
      let formData = new FormData();

      // 添加一般字段
      Object.keys(sendData).forEach((key) => {
        if (key !== "image" && key !== "video") {
          formData.append(key, sendData[key]);
        }
      });

      if (withFile) {
        // 處理 image 和 video，確保它們是列表
        if (Array.isArray(sendData.image)) {
          sendData.image.forEach((file: any, index: any) => {
            formData.append(`image[${index}]`, file);
          });
        } else {
          formData.append(`image[0]`, "null");
        }

        if (Array.isArray(sendData.video)) {
          sendData.video.forEach((file: any, index: any) => {
            formData.append(`video[${index}]`, file);
          });
        } else {
          formData.append(`video[0]`, "null");
        }
      }

      // tags
      if (Array.isArray(sendData.tags)) {
        sendData.tags.forEach((tag: any, index: any) => {
          formData.append(`tag[${index}]`, tag);
        });
      }

      for (var pair of (formData as any).entries()) {
        console.log(pair[0] + ", " + pair[1]);
      }

      try {
        const response = await axios.patch(
          `${config.BACKEND_URL}/technical_orders/orders/${id}`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        // this.$toast?.success("更新成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法更新技令", {});
        }
      }
    },
  },

  getters: {
  },
});
