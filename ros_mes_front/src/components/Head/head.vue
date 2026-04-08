<script setup lang="ts">

</script>

<template>
  <div class="header-container">
    <div class="header-placeholder"></div>
  </div>
</template>

<style scoped>
.header-container {
  width: 100%;
  height: 60px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  margin: 0;
  padding: 0;
  margin-bottom: 20px;
}

.header-placeholder {
  width: 100%;
  height: 100%;
}
</style>