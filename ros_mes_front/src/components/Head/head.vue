<template>
  <div class="header-container">
    <div class="header-left" @click="changeIcon" style="cursor: pointer">
      <el-icon style="margin-right: 10px; transition: transform 0.3s ease;" color="#606266">
        <Fold v-if="layoutSettingStore.fold" />
        <Expand v-else />
      </el-icon>
      <span class="title">机械臂控制系统</span>
    </div>
    <div class="header-right">
      <!-- 可放置用户信息等 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLayoutSettingStore } from '@/stores/layoutSetting';
import { Expand, Fold } from '@element-plus/icons-vue';

const layoutSettingStore = useLayoutSettingStore();

const changeIcon = () => {
  console.log('toggleFold 被调用, 当前 fold =', layoutSettingStore.fold);
  layoutSettingStore.toggleFold();
  console.log('toggleFold 后 fold =', layoutSettingStore.fold);
};
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  box-sizing: border-box;
}
.header-left {
  display: flex;
  align-items: center;
}
.title {
  font-size: 18px;
  font-weight: bold;
  margin-left: 10px;
}
</style>