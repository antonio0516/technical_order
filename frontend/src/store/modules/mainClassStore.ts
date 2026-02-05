import { defineStore } from "pinia";
import axios from "axios";
import { authStore } from "@store/authStore";
import { config } from "@/config";
import { getCurrentInstance, reactive } from "vue";

export const useMainClassStore = defineStore("mainClassStore", {
  state: () => ({
    // items: [] as Item[],
    items: [] as any[],
    subClasses: [] as any[],
    optionClasses: [] as any[],
    filterSubClasses: [] as any[],
    $toast: getCurrentInstance()?.appContext.config.globalProperties.$toast,
    selectedMainClass: reactive({ original_id: "all", _id: "all" as string, name: "全部" }) as any,
    originalMainClassId : reactive({original_id: "all"}) as any, 
    selectedSubClass: reactive({ main_class: "all", sub_class: "全部" }) as any,
    selectedOptionClass: reactive({ option_class: "全部",}) as any,
    filterOptionClasses: [] as any[], // 新增一個選項篩選的資料
    entryLoading: false,
    subClassEntryLoading: false,
    editMainClass: reactive({
      _id: "",
      name: "",
    }) as any,
    editSubClasses: [] as any[],
  }),
  actions: {
    async init() {
      try {
        // get items from backend
        this.entryLoading = true;

        const response = await axios.get(
          `${config.BACKEND_URL}/technical_orders/option_classes_v2`, //這裡要改一下
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        await this.updateSubClasses(this.selectedMainClass._id);
        this.items = response.data;
        console.log(this.items);
        // sort by name
        this.items.sort((a: any, b: any) => {
          return a.name.localeCompare(b.name);
        });
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法取得主目錄", {});
        }
      }
      this.entryLoading = false;
    },

    async addItem(className: string) {
      try {


        const response = await axios.post(
          `${config.BACKEND_URL}/technical_orders/main_classes`,
          {
            main_class: className,
          },
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );

        await this.init();
        await this.updateSubClasses(this.selectedMainClass._id);
        this.$toast?.success("成功添加主目錄");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法添加主目錄", {});
        }
      }
    },
    async deleteItem(id: string) {
      try {
        const response = await axios.delete(
          `${config.BACKEND_URL}/technical_orders/main_classes/${id}`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );

        if (this.selectedMainClass._id == id) {
          this.selectedMainClass = { _id: "all", name: "全部" };
          this.selectedSubClass = { main_class: "all", sub_class: "全部" };
        }
        await this.init();
        this.$toast?.success("刪除成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法刪除主目錄", {});
        }
      }
    },
    async updateItem(id: string, className: string) {
      try {
        const response = await axios.patch(
          `${config.BACKEND_URL}/technical_orders/main_classes/${id}`,
          {
            main_class: className,
          },
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );

        await this.init();
        await this.updateSubClasses(this.selectedMainClass._id);
        this.$toast?.success("更新成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法更新主目錄", {});
        }
      }
    },

    async addSubClass(mainClassId: string, subClassName: string) {
      try {
        const response = await axios.post(
          `${config.BACKEND_URL}/technical_orders/main_classes/${mainClassId}/sub_classes`,
          {
            sub_class: subClassName,
          },
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );

        await this.updateSubClasses(mainClassId);
        this.$toast?.success("成功添加次目錄");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法添加次目錄", {});
        }
      }
    },
////////////////////////////////////  下次須完成所在地 //////////////////////////////////////
    async updateSubClasses(id: string) {
      try {
        this.subClassEntryLoading = true;
        const response = await axios.get(
          `${config.BACKEND_URL}/technical_orders/option_classes_v2/${id}/sub_class`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        console.log("後端回傳的次目錄資料:", response.data);
        this.subClasses = response.data;
        // sort by name
        this.subClasses.sort((a: any, b: any) => {
          return (a.sub_class || "").localeCompare(b.sub_class || "");
        });
        

        if (id != "all") {
          this.filterSubClasses = this.subClasses;
        } else {
          this.filterSubClasses = [];
        }
        this.filterSubClasses.unshift({
          main_class: "all",
          sub_class: "全部",
        });

        console.log("updateSubClasses");
        console.log(this.subClasses);
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法取得次目錄", {});
        }
      }
      this.subClassEntryLoading = false;
    },
    async updateOptionClasses(originalId: string, subClass: string) {
      try {
          const response = await axios.get(
              `${config.BACKEND_URL}/technical_orders/option_classes_v2/${originalId}/${subClass}/option_class`,
              {
                  headers: {
                      Authorization: `Bearer ${authStore().getToken}`,
                  },
              }
          );
          
          console.log("🔍 後端回傳的option資料!!!:", JSON.stringify(response.data, null, 2));
  
          // 🔹 確保 response.data 不是空的
          if (!response.data || response.data.length === 0) {
              console.warn("⚠️ 後端回傳空的選項資料，確保後端查詢有正確匹配");
          }
  
          // 🔹 確保 option_class 只有物件陣列，並展開內部的選項
          this.filterOptionClasses = response.data.flatMap((item: any) => 
              item.option_class.map((option: string) => ({
                  option_class: option
              }))
          );
  
          // 🔹 確保至少有 "全部" 選項
          this.filterOptionClasses.unshift({ option_class: "全部" });
  
          console.log("🛠 更新後的選項:", this.filterOptionClasses);
  
      } catch (error: any) {
          try {
              console.log("錯誤狀態碼:", error.response.status);
              this.$toast?.error(error.response.data.detail, {});
          } catch (error: any) {
              this.$toast?.error("後臺發生錯誤，無法取得選項目錄", {});
          }
      }
    },
    async selectSubClass(mainClassId: string, subClass: string) {
      this.selectedSubClass.main_class = mainClassId;
      this.selectedSubClass.sub_class = subClass;
    
      // 新增這行
      await this.updateOptionClasses(mainClassId, subClass);
    },
    async patchSubClass(
      mainClassId: string,
      oldSubClass: string,
      newSubClass: string
    ) {
      try {
        const response = await axios.patch(
          `${config.BACKEND_URL}/technical_orders/main_classes/${mainClassId}/sub_classes`,
          {
            old_sub_class: oldSubClass,
            new_sub_class: newSubClass,
          },
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );

        if (this.selectedSubClass.sub_class == oldSubClass) {
          this.selectedSubClass = {
            main_class: this.selectedMainClass._id,
            sub_class: newSubClass,
          };
        }

        await this.updateSubClasses(this.selectedMainClass._id);
        this.$toast?.success("更新成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法更新次目錄", {});
        }
      }
    },

    async deleteSubClass(mainClassId: string, subClass: string) {
      try {
        const response = await axios.delete(
          `${config.BACKEND_URL}/technical_orders/main_classes/${mainClassId}/sub_classes/${subClass}`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        if (this.selectedSubClass.sub_class == subClass) {
          this.selectedSubClass = {
            main_class: this.selectedMainClass._id,
            sub_class: "全部",
          };
        }
        await this.updateSubClasses(this.selectedMainClass._id);
        this.$toast?.success("刪除成功");
        return true;
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法刪除次目錄", {});
        }
      }
    },

    async selectMainClass(id: string) {
      this.selectedMainClass._id = id;
      try {
        this.subClassEntryLoading = true;
        const response = await axios.get(
          `${config.BACKEND_URL}/technical_orders/option_classes_v2/${id}`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        console.log("✅ 更新 subClasses:", this.subClasses);
        if (response.data.length > 0) {
          const selectedItem = response.data.find((item: any) => item._id === id);
          this.selectedMainClass.original_id = selectedItem?.original_id || "all";
        } else {
          this.selectedMainClass.original_id = "all";
        }
    
        this.subClasses = [];

        if (Array.isArray(response.data) && response.data.length > 0) {       //讓原本是物件的subclass變成陣列
          const target = response.data[0];  // 只抓第一個主目錄（通常只回傳一筆）
          if (target.sub_classes && Array.isArray(target.sub_classes)) {
            this.subClasses = target.sub_classes.map((item: any) => ({
              sub_class: item.sub_class,
            }));
          }
        }
        console.log("更新 我要檢查subClass:", this.subClasses);
      } catch (error: any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return [];
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法選擇主目錄", {});
        }
      }
      this.subClassEntryLoading = false;
    },

    async selectEditMainClass(id: string) {
      this.editMainClass._id = id;
      try {
        const response = await axios.get(
          `${config.BACKEND_URL}/technical_orders/main_classes/${id}/sub_classes`,
          {
            headers: {
              Authorization: `Bearer ${authStore().getToken}`,
            },
          }
        );
        console.log(response.data);
        // update editSubClasses
        // keep "sub_class" only
        // sub_calss = [
        //   {
        //     "sub_class": "sub_class1"
        //   },
        //   {
        //     "sub_class": "sub_class2"
        //   }
        // ]
        this.editSubClasses = response.data.map((item: any) => {
          return item.sub_class;
        });
      } catch (error: any) {
        try {
          console.log(error);
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return [];
        } catch (error: any) {
          console.log(error);
          this.$toast?.error("後臺發生錯誤，無法選擇主目錄", {});
        }
      }
    },
  },

  getters: {
    getItems(): any[] {
      return this.items;
    },
    getSubClasses(): any[] {
      return this.subClasses;
    },
    getOptionClasses(): any[] {
      return this.filterOptionClasses;
    },
    getItemsWithAll(): any[] {
      return [{ origin_id: "all", _id: "all", name: "全部" }, ...this.items];  //修改於2025
    },
    getSelectedMainClass(): string {
      return this.selectedMainClass;
    },
    getSelectedSubClass(): string {
      return this.selectedSubClass;
    },
  },
});
