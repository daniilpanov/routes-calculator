import "@/styles/bootstrap-imports.scss";
import * as bootstrap from "bootstrap";

import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.provide("bootstrap", bootstrap);

app.mount("#app");
