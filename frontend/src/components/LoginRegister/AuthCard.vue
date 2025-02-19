<script setup lang="ts">
import LoginCard from "@/components/LoginRegister/LoginCard.vue";
import RegisterCard from "@/components/LoginRegister/RegisterCard.vue";
import ForgetPasswordCard from "@/components/LoginRegister/ForgetPasswordCard.vue";
import { shallowRef } from "vue";

let currentView: any = shallowRef(LoginCard);

const switchAuthView = (view: string) => {
  console.log(view);
  switch (view) {
    case "login":
      currentView.value = LoginCard;
      break;
    // case "register":
    //   currentView.value = RegisterCard;
    //   break;
    // case "forget-password":
    //   currentView.value = ForgetPasswordCard;
    //   break;
  }
};
</script>

<template>
  <component :is="currentView" @switchAuthView="switchAuthView" />
</template>

<style scoped>
</style>
