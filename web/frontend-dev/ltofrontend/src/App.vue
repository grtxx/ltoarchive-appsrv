<template>
  <div style="position:fixed;">
    <sidebar-menu :menu="menu">

    </sidebar-menu>
  </div>
  <div style="margin-left: 64px;">
    <RouterView></RouterView>
  </div>
</template>

<script>
//import AppWindow from './components/appwindow.vue'
import { SidebarMenu } from 'vue-sidebar-menu'

export default {
  name: 'App',
  components: {
    SidebarMenu
  },
  data: function() {
    return {
      menu: [
        {
          header: "LTO browser",
          hiddenOnCollapse: true,
        },
        {
          href: "/",
          title: 'Browse',
          icon: 'fa fa-browse'
        },
        {
          href: "Search",
          title: 'Search',
          icon: 'fa fa-browse'
        },
        {
          href: "Jobs",
          title: 'Jobs',
          icon: 'fa fa-job'
        }
      ]
    };
  },
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
