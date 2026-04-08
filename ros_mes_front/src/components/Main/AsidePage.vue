<!-- eslint-disable -->
<template>
  <div class="aside-container">
    <div class="aside-header">
      <h2 class="aside-title">MES核心控制台</h2>
    </div>
    <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical-demo"
        @select="handleMenuSelect"
        background-color="#2b3243"
        active-text-color="#ffd04b"
        text-color="#fff"
    >
      <el-menu-item index="/HardWorkPage">
        <el-icon><icon-menu /></el-icon>
        <span>设备信息管理</span>
      </el-menu-item>
      <el-menu-item index="/ModuleManagement">
        <el-icon><document /></el-icon>
        <span>模块管理</span>
      </el-menu-item>
      <el-menu-item index="/FineTuningPage">
        <el-icon><setting /></el-icon>
        <span>微调模块</span>
      </el-menu-item>
    </el-menu>
    <div class="aside-footer">
      <!-- 自定义长按急停按钮 -->
      <div
          class="emergency-stop-wrapper"
          :class="{ 'long-pressing': isPressing }"
          @mousedown="startLongPress"
          @mouseup="cancelLongPress"
          @mouseleave="cancelLongPress"
          @touchstart="startLongPress"
          @touchend="cancelLongPress"
          @touchcancel="cancelLongPress"
      >
        <div class="progress-bar" :class="{ 'active': isPressing }"></div>
        <span class="btn-text">长按两秒急停</span>
      </div>
    </div>
  </div>

  <!-- 急停遮罩层 -->
  <div v-if="isEmergencyActive" class="emergency-overlay">
    <div class="emergency-content">
      <h1 style="color: white;">SYSTEM EMERGENCY STOP</h1>
      <h1 style="color: white;">系统已触发急停</h1>
      <el-button type="danger" @click="resetEmergency" class="reset-button">解除急停 (仅调试)</el-button>
    </div>
  </div>
</template>

<script setup>
import {
  Document,
  Menu as IconMenu,
  Setting,
} from '@element-plus/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import { computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

const router = useRouter();
const route = useRoute();

const activeMenu = computed(() => route.path);
const handleMenuSelect = (index) => {
  router.push(index);
};

// ========== 急停长按逻辑 ==========
const isPressing = ref(false);         // 是否正在长按（用于触发进度条动画）
const isEmergencyActive = ref(false);  // 急停状态
let pressTimer = null;                 // 长按定时器
const LONG_PRESS_DURATION = 2000;      // 2秒

// 开始长按
const startLongPress = (event) => {
  if (isEmergencyActive.value) return; // 急停中不允许再次触发

  // 阻止默认事件（避免移动端页面滚动）
  event.preventDefault();
  if (pressTimer) clearTimeout(pressTimer);
  
  // 标记正在长按，CSS 进度条开始过渡动画（通过 transition 实现平滑填充）
  isPressing.value = true;
  
  // 设置长按定时器，2秒后触发急停
  pressTimer = setTimeout(() => {
    if (isPressing.value) {
      triggerEmergency();
    }
    // 清理状态
    isPressing.value = false;
    pressTimer = null;
  }, LONG_PRESS_DURATION);
};

// 取消长按（提前松开）
const cancelLongPress = () => {
  if (pressTimer) {
    clearTimeout(pressTimer);
    pressTimer = null;
  }
  isPressing.value = false;
};

// 触发急停
const triggerEmergency = async () => {
  console.log('[模拟] 急停指令已触发');
  ElMessage.warning('急停指令已触发，所有机械臂停止运动');
  isEmergencyActive.value = true;

  // 重置长按状态，避免进度条卡在100%
  cancelLongPress();

  // 5秒后自动关闭遮罩（符合文档“画面变红5秒”）
  setTimeout(() => {
    if (isEmergencyActive.value) {
      isEmergencyActive.value = false;
      ElMessage.info('系统已恢复，请谨慎操作');
    }
  }, 5000);

  // 真实接口（后端就绪后取消注释）
  /*
  try {
    await request.post('/stop', { status: 0 });
    console.log('急停指令已发送至ROS');
    ElMessage.success('急停指令已执行');
  } catch (err) {
    console.error('急停接口调用失败', err);
    ElMessage.error('急停指令发送失败');
  }
  */
};

// 解除急停（仅调试用）
const resetEmergency = () => {
  isEmergencyActive.value = false;
  ElMessage.info('急停已解除');
};
</script>

<style scoped>
.aside-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2b3243;
  margin: 0;
  padding: 0;
}

.aside-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.aside-title {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  text-align: center;
}

.el-menu-vertical-demo {
  flex: 1;
  height: 100%;
  border-right: none;
  border-left: none;
}

.aside-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 自定义长按急停按钮样式 */
.emergency-stop-wrapper {
  position: relative;
  width: 100%;
  height: 50px;
  background-color: #f56c6c;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  user-select: none;
  transition: transform 0.08s linear; /* 让缩放变化更跟手 */
}

/* 按下时的缩放效果 */
.emergency-stop-wrapper:active,
.emergency-stop-wrapper.long-pressing {
  transform: scale(0.9);
  transition: transform 0.1s ease;
}

/* 进度条 - 默认宽度 0，通过 active class 触发过渡动画到 100% */
.progress-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background-color: #880000;
  width: 0%;
  transition: width 0s linear; /* 默认无过渡，避免瞬间变化 */
  pointer-events: none;
}

/* 长按激活时，进度条宽度过渡到 100%，时长等于长按时间 */
.progress-bar.active {
  width: 100%;
  transition: width 2s linear; /* 2秒内从0%平滑到100% */
}

.btn-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: white;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 2px;
  transition: color 0.3s ease;
}

.emergency-stop-wrapper:hover .btn-text {
  color: #4f9eff;
}

/* 消除el-aside的默认样式影响 */
:deep(.el-aside) {
  padding: 0;
  margin: 0;
}

/* 急停遮罩层样式 */
.emergency-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #df3b3b;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.5s ease-in-out;
}

.emergency-content {
  text-align: center;
  color: white;
  padding: 40px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.emergency-content h1 {
  font-size: 36px;
  margin-bottom: 20px;
  font-weight: bold;
  letter-spacing: 2px;
}

.reset-button {
  font-size: 16px;
  padding: 20px 36px;
  margin-top: 20px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>