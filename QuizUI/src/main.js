import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "./assets/main.css";
import {createVuetify} from "vuetify";
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
const app = createApp(App);

app.use(router);
app.use(createVuetify({components,directives}));

app.mount("#app");
