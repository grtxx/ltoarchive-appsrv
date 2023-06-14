import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import FileBrowser from './components/FileBrowser.vue'
import PrimeVue from 'primevue/config';
import { SidebarMenu } from 'vue-sidebar-menu';
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

//import "primevue/resources/themes/lara-light-indigo/theme.css";
 
const routes = [
    { path: '/', component: FileBrowser },
    //{ path: '/about', component: FileBrowser },
  ]

const router = createRouter( {
    history: createWebHashHistory(),
    routes: routes,
} );

const app = createApp( App )
app.use(router)
app.use(PrimeVue);
app.use(SidebarMenu);
app.mount('#app')

