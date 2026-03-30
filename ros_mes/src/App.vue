<template>
  <router-view/>
</template>

<script>
import Main from './components/Main/MainPage.vue'
export default {
  name: 'App',
  components: {
    Main
  }
}
</script>

<style>
html,body{
  margin: 0;
  padding:0;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
}
#app {
  width: 100%;
  height: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  overflow: auto;
}

</style>
