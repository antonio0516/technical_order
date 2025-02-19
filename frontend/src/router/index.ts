import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      name: "Home",
      component: () => import("/src/views/Home.vue"),
    },
    {
      path: "/technical_order_editor",
      name: "TechnicalOrderEditor",
      component: () => import("/src/views/TechnicalOrderEditor.vue"),
    },
    {
      path: "/function_panel/:index",
      name: "FunctionPanel",
      component: () => import("/src/views/FunctionPanel.vue"),
    },
    {
      path: "/auth_management",
      name: "AuthManagement",
      component: () => import("/src/views/AuthManagement.vue"),
    },
    {
      path: "/exam_management",
      name: "ExamManagement",
      component: () => import("/src/views/ExamManagement.vue"),
    },
    {
      path: "/version_control",
      name: "VersionControl",
      component: () => import("/src/views/VersionControl.vue"),
    },
    {
      path: "/admin_log",
      name: "AdminLog",
      component: () => import("/src/views/AdminLog.vue"),
    }
  ],
});

export default router;
