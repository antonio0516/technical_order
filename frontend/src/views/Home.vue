<script setup lang="ts">
import AuthCard from "@/components/LoginRegister/AuthCard.vue";
import axios from "axios";
import { config } from "@/config";
import { app } from "electron";
import { ref, onMounted, onUnmounted, reactive, watch } from "vue";

// console.log(import.meta.env.VITE_APP_TITLE);
const appTitle = "技令編輯器";
const connectionStatus = ref({
  message: "連線中",
  isConnected: false
});
let intervalId:any = null;
let disconnectTimer: any = null;
const disconnectAdvice = ref("");
const needClearTimer = ref(false);

const setDisconnectTimer = () => {
  if (disconnectTimer) {
    if (needClearTimer.value) {
      clearTimeout(disconnectTimer);
      needClearTimer.value = false;
    } else {
      return;
    }
  }
  disconnectTimer = setTimeout(() => {
    if (!connectionStatus.value.isConnected) {
      disconnectAdvice.value = "連接問題持續存在，請嘗試重開機以重啟後台服務";
    }
    needClearTimer.value = true;
  }, 20000); // Trigger the advice after 20 seconds of disconnection
};

const checkBackend = async () => {
  const res = await axios
    .get(`${config.BACKEND_URL}/`, {})
    .then(response => {
      connectionStatus.value = { message: "已連線", isConnected: true };
      disconnectAdvice.value = ""
    })
    .catch(() => {
      connectionStatus.value = { message: "無法連線", isConnected: false };
      setDisconnectTimer();
    });
};

onMounted(() => {
  intervalId = setInterval(() => {
    checkBackend();
  }, 2000);
});

onUnmounted(() => {
  clearInterval(intervalId);
  clearTimeout(disconnectTimer); // Clear the timer to prevent memory leaks
});
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="5">
        <!-- <div></div> -->
        <auth-card />
      </v-col>
      <v-col cols="7">
        <v-card color="transparent" flat>
          <div class="d-flex justify-center align-center" style="height: 100vh; ">
            <div class="app-title">
              <div>{{ appTitle }}</div>
              <div class="en-app-title" >Technical Order Editor</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
  <!-- v-if="disconnectAdvice" -->
  <v-alert 
      v-if="disconnectAdvice"
      class="disconnection-alert"
      :text="disconnectAdvice"
  ></v-alert>
  <div class="connection-status">
    <span v-if="connectionStatus.message !== '連線中'" :class="{'status-circle': true, 'connected': connectionStatus.isConnected, 'disconnected': !connectionStatus.isConnected}"></span>
    <v-progress-circular width="5" size="20" color="primary" indeterminate v-if="connectionStatus.message === '連線中'"></v-progress-circular>
    {{ connectionStatus.message }}
  </div>
</template>

<style scoped>
.app-title {
  position: absolute;
  font-size: 4.7em;
  color: #ffffff;
  z-index: 2;

  filter: drop-shadow(2px 0px 0px black) drop-shadow(-2px 0px 0px black)
    drop-shadow(0px 2px 0px black) drop-shadow(0px -2px 0px black);
}
.en-app-title {
  font-size: 0.4em;
  color: #ffffff;
  z-index: 2;
}

.connection-status {
  position: fixed;
  right: 1em;
  bottom: 1em;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 1.5em;
}
.disconnection-alert {
  position: fixed;
  right: 1em;
  bottom: 4em;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 1.5em;
}

.status-circle {
  height: 15px;
  width: 15px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 5px;
}
.connected {
  background-color: #4CAF50; /* Green for connected */
}
.disconnected {
  background-color: #f44336; /* Red for disconnected */
}
</style>
