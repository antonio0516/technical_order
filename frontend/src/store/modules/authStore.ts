import { defineStore } from "pinia";

export const authStore = defineStore("authStore", {
  state: () => ({
    token: "",
  }),
  actions: {
    setToken(token: string) {
      this.token = token;
    },
  },

  getters: {
    getToken(): string {
      return this.token;
    }
  },
});
