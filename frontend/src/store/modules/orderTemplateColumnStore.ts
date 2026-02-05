import { defineStore } from "pinia";
import axios from "axios";
import { authStore } from "@store/authStore";
import { config } from "@/config";
import { getCurrentInstance } from "vue";

export const useOrderTemplateColumnStore = defineStore(
  "orderTemplateColumnStore",
  {
    state: () => ({
      items: [] as any[],
      $toast: getCurrentInstance()?.appContext.config.globalProperties.$toast,
      sortOrder: [
        "步驟名稱",
        "step 步驟",
        "主目錄",
        "次目錄",
        "選項",
        "輔助圖片",
        "輔助影片",
        "輔助 PDF",
      ],
      entryLoading: false,
    }),
    actions: {
      async init() {
        try {
          this.entryLoading = true;
          // get items from backend
          const response = await axios.get(
            `${config.BACKEND_URL}/technical_orders/order_template_columns`,
            {
              headers: {
                Authorization: `Bearer ${authStore().getToken}`,
              },
            }
          );

          this.items = response.data;
          this.items.sort((a: any, b: any) => {
            let indexA = this.sortOrder.indexOf(a.name);
            let indexB = this.sortOrder.indexOf(b.name);

            if (indexA === -1) indexA = this.sortOrder.length;
            if (indexB === -1) indexB = this.sortOrder.length;

            return indexA - indexB;
          });
          this.entryLoading = false;
        } catch (error: any) {
          try {
            console.log(error.response.status);
            this.$toast?.error(error.response.data.detail, {});
            return false;
          } catch (error: any) {
            this.$toast?.error("後臺發生錯誤，無法取得欄位", {});
          }
        }
      },

      async addItem(columnName: string, columnType: string) {
        try {
          const response = await axios.post(
            `${config.BACKEND_URL}/technical_orders/order_template_columns`,
            {
              name: columnName,
              type: columnType,
            },
            {
              headers: {
                Authorization: `Bearer ${authStore().getToken}`,
              },
            }
          );

          await this.init();
          this.$toast?.success("成功添加欄位");
          return true;
        } catch (error: any) {
          try {
            console.log(error.response.status);
            this.$toast?.error(error.response.data.detail, {});
            return false;
          } catch (error: any) {
            this.$toast?.error("後臺發生錯誤，無法添加欄位", {});
          }
        }
      },
      async deleteItem(id: string) {
        try {
          const response = await axios.delete(
            `${config.BACKEND_URL}/technical_orders/order_template_columns/${id}`,
            {
              headers: {
                Authorization: `Bearer ${authStore().getToken}`,
              },
            }
          );

          await this.init();
          this.$toast?.success("刪除成功");
          return true;
        } catch (error: any) {
          try {
            console.log(error.response.status);
            this.$toast?.error(error.response.data.detail, {});
            return false;
          } catch (error: any) {
            this.$toast?.error("後臺發生錯誤，無法刪除欄位", {});
          }
        }
      },
      async updateItem(id: string, columnName: string) {
        try {
          const response = await axios.patch(
            `${config.BACKEND_URL}/technical_orders/order_template_columns/${id}`,
            {
              new_column_name: columnName,
            },
            {
              headers: {
                Authorization: `Bearer ${authStore().getToken}`,
              },
            }
          );

          await this.init();
          this.$toast?.success("更新成功");
          return true;
        } catch (error: any) {
          try {
            console.log(error.response.status);
            this.$toast?.error(error.response.data.detail, {});
            return false;
          } catch (error: any) {
            this.$toast?.error("後臺發生錯誤，無法更新欄位", {});
          }
        }
      },
    },

    getters: {
      getItems(): any[] {
        return this.items;
      },
    },
  }
);
