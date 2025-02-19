<script setup lang="ts">
import axios from "axios";
import { config } from "@/config";
import { ref, onMounted, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
// toast
import "vue3-toastify/dist/index.css";

const router = useRouter();
const $toast = getCurrentInstance()?.appContext.config.globalProperties.$toast;
let failedAttempts = ref(1);

const checkBackend = async () => {
  const res = await axios
    .get(`${config.BACKEND_URL}/`, {})
    .then(response => {
      failedAttempts.value = 0; // 重置失敗計數器
    })
    .catch(() => {
      failedAttempts.value++;
      if (failedAttempts.value >= 3) {
        router.push("/");
        $toast?.error("無法連線到後端伺服器", {});
        failedAttempts.value = 0;
      }
    });
};

onMounted(() => {
  setInterval(() => {
    checkBackend();
  }, 3000);
});
</script>

<template>
  <div class="app-wrap">
    <div class="app-bg"></div>
    <router-view></router-view>
  </div>
</template>

<style>
.vjs-icon-play,
.video-js .vjs-big-play-button .vjs-icon-placeholder:before,
.video-js .vjs-play-control .vjs-icon-placeholder,
.vjs-icon-fullscreen-enter,
.video-js .vjs-fullscreen-control .vjs-icon-placeholder,
.vjs-icon-volume-high,
.video-js .vjs-mute-control .vjs-icon-placeholder {
  font-family: VideoJS !important;
  font-weight: normal;
  font-style: normal;
}

@font-face {
  font-family: "NotoSansTCLight";
  src: url("@/fonts/NotoSansTC-Light.ttf") format("truetype");
}

@font-face {
  font-family: "NotoSansTCExtraLight";
  src: url("@/fonts/NotoSansTC-ExtraLight.ttf") format("truetype");
}

@font-face {
  font-family: "TWKaiExtB";
  src: url("@/fonts/TW-Kai-Ext-B-98.ttf") format("truetype");
}

@font-face {
  font-family: "TWKai";
  src: url("@/fonts/TW-Kai-98_1.ttf") format("truetype");
}

* {
  font-family: "TWKai" !important;
  font-size: 1.05em;
}

/* background */

.app-bg {
  opacity: 0.9;
  position: absolute;
  left: 0;
  top: 0;
  /* width: 100%; */
  height: 100%;
  width: 100%;
  object-fit: cover;
  /* 使圖片覆蓋整個區域 */
  background-image: url("@/assets/background/camouflage-1.png");
  background-repeat: no-repeat;
  background-size: cover;

  /* backgorund color */
}

.app-wrap {
  position: relative;
  overflow: hidden;
  height: 100vh;
  background-color: #ffffff;
}

.v-toast {
  padding: 0.1em !important;
  z-index: 5000 !important;
}

.v-toast__item {
  font-size: 1.3em !important;
  padding: 0.1em !important;
}

.v-toast__text {
  /* no y-axis padding */
  padding: 0.5em 1em !important;
}

.v-toast__item {
  min-height: 3em !important;
  max-width: 50vw !important;
}

/* scroll bar*/
/* custom scrollbar */
::-webkit-scrollbar {
  width: 20px;
  background-color: transparent;
}

::-webkit-scrollbar-track {
  background-color: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cccccc;
  animation: gradient 1s ease infinite;
  border-radius: 20px;
  border: 6px solid transparent;
  background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #aaaaaa;
}

::-webkit-scrollbar {
  display: none;
}

body ::-webkit-scrollbar {
  /* set back to default */
  display: initial;
}

/**/</style>
