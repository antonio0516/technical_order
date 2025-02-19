<script setup lang="ts">
import AuthCard from "@/components/LoginRegister/AuthCard.vue";
import { app } from "electron";
import { ref, onMounted, reactive, watch } from "vue";
import { useRoute } from 'vue-router'

import typingImage from "@/assets/images/panel/typing.jpg";
import lockImage from "@/assets/images/panel/lock.jpg";
import examImage from "@/assets/images/panel/exam.jpg";
import gitImage from "@/assets/images/panel/git.jpg";
import recordImage from "@/assets/images/panel/record.jpg";

// console.log(import.meta.env.VITE_APP_TITLE);
const appTitle = "技令編輯器";
const windowModel = ref(0);

const route = useRoute()

onMounted(() => {
  const index: any = route.params.index;
  windowModel.value = parseInt(index);
})

const panels = [
  {
    // src: "@/assets/images/panel/typing.jpg",
    src: typingImage,
    text: "技令編修",
    route: "/technical_order_editor",
  },
  {
    src: lockImage,
    text: "管理員帳號管理",
    route: "/auth_management",
  },
  {
    src: examImage,
    text: "考試管理",
    route: "/exam_management",
  },
  {
    src: gitImage,
    text: "技令版本控制",
    route: "/version_control",
  },
  {
    src: recordImage,
    text: "使用紀錄",
    route: "/admin_log",
  },
];
</script>

<template>
  <v-container>
    <v-row align="center" style="height: 100vh;">
      <v-col align="center">
        <v-card style="height: 80vh; width: 80vw">
          <v-card-title>
            <v-col align="start">
              <div style="font-size: 1.5em">選擇功能</div>
            </v-col>
            <v-divider class="my-2 mb-7"></v-divider>
          </v-card-title>
          <v-card-text>
            <v-carousel  show-arrows style="width: 65vw; height: 70vh" hide-delimiters>
              <template v-slot:prev="{ props }">
                <v-btn  color="primary" @click="props.onClick" icon="mdi-chevron-left"></v-btn>
              </template>
              <template v-slot:next="{ props }">
                <v-btn  color="primary" @click="props.onClick"
                  icon="mdi-chevron-right"></v-btn>
              </template>
              <v-carousel-item v-for="(panel, i) in panels" :key="i" style="height: 70vh">
                <v-card class="mx-5" style="width: 50vw;height: 70vh">
                  <v-btn width="50vw" height="60vh"  :ripple="false">
                    <v-img :src="panel.src" class="align-end" gradient="to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.8)"
                      width="50vw" height="60vh" cover @click="() => $router.push(panel.route)">
                      <div class="text-white ma-3 text-border pa-2" style="font-size: 2.5em">
                        {{ panel.text }}
                      </div>
                    </v-img>
                  </v-btn>
                </v-card>
              </v-carousel-item>
            </v-carousel>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style>
.text-border {
  z-index: 2;

  filter: drop-shadow(1px 0px 0px black) drop-shadow(-1px 0px 0px black) drop-shadow(0px 1px 0px black) drop-shadow(0px -1px 0px black);
}
</style>
