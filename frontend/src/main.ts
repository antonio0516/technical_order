import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "./samples/node-api";

import "vuetify/styles";
import { createVuetify } from "vuetify";
// import { aliases, mdi } from "vuetify/iconsets/mdi";
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import VueNumberInput from '@chenfengyuan/vue-number-input';

import InfiniteLoading from "v3-infinite-loading";
import "v3-infinite-loading/lib/style.css"; //required if you're not going to override default slots

import router from "./router";
import pinia from "./store";
import axios from "axios";
import VueAxios from "vue-axios";
import Vue3Toastify, { type ToastContainerOptions } from "vue3-toastify";
import { VDateInput } from 'vuetify/labs/VDateInput';

import VueVideoPlayer from "@videojs-player/vue";
import "video.js/dist/video-js.css";

import ToastPlugin from "vue-toast-notification";
import "vue-toast-notification/dist/theme-bootstrap.css";

const customColorTheme = {
  dark: true,
  colors: {
    primary: "#566be7",
    primary_lighter: "#7c8fff",
    secondary: "#acc4ca",
    card_in_card: "#121212",
    card_in_card_bar: "aaaaaa",
  },
};

const vuetify = createVuetify({
  components: {
    VDateInput,
    ...components,
  },
  directives,
  theme: {
    defaultTheme: "customColorTheme",
    themes: {
      customColorTheme,
    },
  },
});

const app = createApp(App)
  .use(VueVideoPlayer)
  .use(router)
  .use(pinia)
  .use(vuetify)
  .use(VueAxios, axios)
  // .use(Vue3Toastify, {
  //   autoClose: 3000,
  //   theme: "dark",
  //   position: "top-center",
  //   transition: "flip",
  // } as ToastContainerOptions)
  .use(ToastPlugin, {
    duration: 2000,
    position: "top",
  })
  .component("infinite-loading", InfiniteLoading)
  .component(VueNumberInput.name!, VueNumberInput)
  .mount("#app")
  .$nextTick(() => {
    postMessage({ payload: "removeLoading" }, "*");
  });
