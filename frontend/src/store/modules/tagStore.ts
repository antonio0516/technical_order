import { defineStore } from "pinia";
import axios from "axios";
import { authStore } from "@store/authStore";
import { config } from "@/config";
import { getCurrentInstance, reactive } from "vue";

export const useTagStore = defineStore("tagStore", {
  state: () => ({
    selectedTags: [] as any[],
    tags: [] as any[],
    $toast: getCurrentInstance()?.appContext.config.globalProperties.$toast,
    entryLoading: false,
  }),
  actions: {
    async addTag(newTagName: string) {
      console.log(`${config.BACKEND_URL}/technical_orders/tags`);
      const res = await axios.post(
        `${config.BACKEND_URL}/technical_orders/tags`,
        { name: newTagName },
        { headers: { Authorization: `Bearer ${authStore().getToken}` } }
      );
      await this.updateTagItems();
    },
    async updateTagItems() {
      try {
        this.entryLoading = true;
        const res = await axios.get(
          `${config.BACKEND_URL}/technical_orders/tags`,
          {
            headers: { Authorization: `Bearer ${authStore().getToken}` },
          }
        );

        this.tags = res.data;
        // sort by name
        this.tags.sort((a: any, b: any) => {
          return a.name.localeCompare(b.name);
        });
      } catch (error:any) {
        try {
          console.log(error.response.status);
          this.$toast?.error(error.response.data.detail, {});
          return false;
        } catch (error: any) {
          this.$toast?.error("後臺發生錯誤，無法取得標籤", {});
        }
      }
      this.entryLoading = false;
    },
    async deleteTag(id: string) {
      await axios.delete(`${config.BACKEND_URL}/technical_orders/tags/${id}`, {
        headers: { Authorization: `Bearer ${authStore().getToken}` },
      });
      if (this.selectedTags.includes(id)) {
        this.selectedTags = this.selectedTags.filter((tag) => tag !== id);
      }
      await this.updateTagItems();
    },
    async updateTag(id: string, name: string) {
      await axios.patch(
        `${config.BACKEND_URL}/technical_orders/tags/${id}`,
        { name: name },
        {
          headers: { Authorization: `Bearer ${authStore().getToken}` },
        }
      );
      await this.updateTagItems();
    },
  },

  getters: {
    getTags(): any[] {
      return this.tags;
    },
  },
});
