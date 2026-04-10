<template>
  <div class="fine-tuning-container">
    <!-- 顶部静态文字和按钮 -->
    <div class="header-bar">
      <div class="header-left">
        <el-button type="default" @click="goBack" class="back-button">
          &lt; Back
        </el-button>
        <span class="header-title">机械臂姿态微调与压力监控</span>
      </div>
    </div>
    <div class="header-right">
        <el-button type="primary" @click="handleRosConnect">ROS连接</el-button>
        <el-button type="success" @click="handleSaveConfig">保存配置</el-button>
        <el-button type="warning" @click="resetAllAdjust">重置参数</el-button>
        <el-button type="info" @click="handleHistory">历史记录</el-button>
      </div>



    <!-- ========== 2. 三个机械臂的微调面板 ========== -->
    <!-- <div class="arm-list">
      <el-card
          v-for="arm in armList"
          :key="arm.id"
          :header="`机械臂 ${arm.idHex}`"
          shadow="hover"
          class="arm-card"
      >
        <el-form label-width="140px" > -->
          <!-- 旋转轴 -->
          <!-- <el-form-item label="底座旋转调整值" >
            <el-input-number
                v-model="arm.adjust.rotate"
                :min="-360" :max="360"
                placeholder="顺时针为正"
                @change="sendSingleAdjust(arm)"
            />
            <span class="current-value">当前实际值: {{ arm.current.rotate }}°</span>
          </el-form-item> -->

          <!-- 摆动轴 -->
          <!-- <el-form-item label="摆动调整值">
            <el-input-number
                v-model="arm.adjust.swing"
                :min="-90" :max="90"
                @change="sendSingleAdjust(arm)"
            />
            <span class="current-value">当前实际值: {{ arm.current.swing }}°</span>
          </el-form-item> -->

          <!-- 伸缩杆 -->
          <!-- <el-form-item label="伸缩杆调整值">
            <el-input-number
                v-model="arm.adjust.telescope"
                :min="-20" :max="20"
                :step="0.5"
                @change="sendSingleAdjust(arm)"
            />
            <span class="current-value">当前实际值: {{ arm.current.telescope }}cm</span>
          </el-form-item> -->

          <!-- 单个机械臂下发按钮 -->
<!--          <el-form-item>-->
<!--            <el-button type="primary" @click="sendSingleAdjust(arm)">下发微调</el-button>-->
<!--          </el-form-item>-->
        <!-- </el-form> -->

        <!-- 压力传感器信息 -->
        <!-- <div class="pressure-sensor">
          <span class="pressure-label">压力传感器：</span>
          <span class="pressure-value">-- (等待接入)</span>
        </div>

      </el-card>
    </div> -->



    <!-- ======机械臂的微调面板======== -->

    <div class="arm-list">
      <el-card
          v-for="arm in armList"
          :key="arm.id"
          shadow="hover"
          class="main-control-card"
      >
        <template #header>
          <div class="card-header">
            <span class="header-text">核心机械臂控制单元 - 设备 {{ arm.idHex }}</span>
            <el-tag type="success" effect="dark" round size="small">运行中</el-tag>
          </div>
        </template>

        <div class="control-grid">
          <div class="control-item">
            <div class="label-box">
              <span class="label-title">底座旋转调整值</span>
              <span class="real-time-tag">当前实际值: {{ arm.current.rotate }}°</span>
            </div>
            <div class="input-wrapper">
              <el-input-number
                  v-model="arm.adjust.rotate"
                  :min="-360" :max="360"
                  placeholder="顺时针为正"
                  @change="sendSingleAdjust(arm)"
              />
             
            </div>
          </div>

          <div class="control-item">
            <div class="label-box">
              <span class="label-title">摆动调整值</span>
              <span class="real-time-tag">当前实际值: {{ arm.current.swing }}°</span>
            </div>
            <div class="input-wrapper">
              <el-input-number
                  v-model="arm.adjust.swing"
                  :min="-90" :max="90"
                  @change="sendSingleAdjust(arm)"
              />
             
            </div>
          </div>

          <div class="control-item">
            <div class="label-box">
              <span class="label-title">伸缩杆调整值</span>
              <span class="real-time-tag">当前实际值: {{ arm.current.telescope }}cm</span>
            </div>
            <div class="input-wrapper">
              <el-input-number
                  v-model="arm.adjust.telescope"
                  :min="-20" :max="20"
                  :step="0.5"
                  @change="sendSingleAdjust(arm)"
              />
              
            </div>
          </div>
        </div>

        <div class="sensor-panel">
          <div class="sensor-title">压力传感器实时反馈</div>
          <div class="sensor-value-box">
            <span class="status-dot pulse"></span>
            <span class="value-text">等待数据接入...</span>
          </div>
        </div>

      </el-card>
    </div>


    <!-- ========== 3. 批量操作栏 ========== -->
    <div class="batch-bar">
<!--      <el-button type="success" @click="sendBatchAdjust">批量下发所有机械臂</el-button>-->
      <el-button @click="resetAllAdjust">重置所有调整值</el-button>
    </div>


    <el-dialog
      v-model="initDialogVisible"
      title="配置设备参数"
      width="450px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <el-form label-width="100px">
        <el-form-item label="设备编号" required>
          <el-select v-model="initConfig.deviceId" placeholder="请选择机械臂" style="width: 100%">
            <!-- <el-option label="当前坐标设备 (0)" :value="0" /> -->
            <el-option label="机械臂1 (0x20)" :value="0x20" />
            <!-- <el-option label="机械臂2 (0x40)" :value="0x40" />
            <el-option label="机械臂3 (0x60)" :value="0x60" /> -->
          </el-select>
        </el-form-item>
        <el-form-item label="X 坐标" required>
          <el-input-number v-model="initConfig.x" :step="10" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Y 坐标" required>
          <el-input-number v-model="initConfig.y" :step="10" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Z 坐标" required>
          <el-input-number v-model="initConfig.z" :step="10" controls-position="right" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="confirmInitConfig">确定并关闭</el-button>
      </template>
    </el-dialog>

  </div> </template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

const router = useRouter();



// ========== 新增：初始化强制弹窗逻辑 ==========
const initDialogVisible = ref(true); // 默认 true，页面一进来就弹
const initConfig = reactive({
  // deviceId: null as number | null,
  deviceId: 0x20,
  x: 0,
  y: 0,
  z: 0
});

const confirmInitConfig = () => {
  if (initConfig.deviceId === null) {
    ElMessage.warning('必须选择一个设备编号才能继续');
    return;
  }
  
  // 将用户选中的设备ID赋值给微调页面原有的变量，让微调页面可以正常工作
  currentDeviceId.value = initConfig.deviceId;
  
  // 在这里你可以直接调用后端接口下发 XYZ 坐标
  console.log('初始位置已下发:', initConfig);
  ElMessage.success('初始参数设置成功！');
  
  // 关闭弹窗
  initDialogVisible.value = false;
};

// ========== 1. 路由参数获取 ==========
const route = useRoute();
const moduleId = ref<number>(0);                // 当前操作的模块编号
const currentDeviceId = ref<number>(0);         // 模块管理页面选中的机械臂编号
const currentDeviceIdHex = computed(() => `0x${currentDeviceId.value.toString(16)}`);

// ========== 2. 机械臂数据定义 ==========
// 每个机械臂包含：
// - id: 设备编号（0x20,0x40,0x60）
// - adjust: 用户输入的待下发增量（角度或长度）
// - current: 机械臂当前实际姿态（从后端获取，此处用模拟初始值）
const armList = reactive([
  {
    id: 0x20,
    idHex: '0x20',
    adjust: { rotate: 0, swing: 0, telescope: 0 },
    current: { rotate: 150, swing: 30, telescope: 25 },   // 模拟初始值
  },
  // {
  //   id: 0x40,
  //   idHex: '0x40',
  //   adjust: { rotate: 0, swing: 0, telescope: 0 },
  //   current: { rotate: 160, swing: 25, telescope: 24 },
  // },
  // {
  //   id: 0x60,
  //   idHex: '0x60',
  //   adjust: { rotate: 0, swing: 0, telescope: 0 },
  //   current: { rotate: 145, swing: 35, telescope: 26 },
  // },
]);

// ========== 3. 单个机械臂微调（核心接口） ==========
// 接口：POST /module
// 参数：{ module_id, device_id, position: [旋转增量, 摆动增量, 伸缩增量] }
const sendSingleAdjust = async (arm: any) => {
  const position = [arm.adjust.rotate, arm.adjust.swing, arm.adjust.telescope];

  // 检查是否有非零调整值
  if (position.every(v => v === 0)) {
    ElMessage.warning('请至少输入一个非零调整值');
    return;
  }

  console.log('微调请求参数:', {
    module_id: moduleId.value,
    device_id: arm.id,
    position
  });

  try {
    const res = await request.post('/module', {
      module_id: moduleId.value,
      device_id: arm.id,
      position
    });

    if (res && res.code === 200) {
      ElMessage.success(`机械臂 ${arm.idHex} 微调成功`);

      // 重要：根据后端返回更新当前实际值（这里假设后端返回新的 current 值）
      // 如果后端返回了新的姿态数据，应使用 res.data 更新
      // 示例：arm.current.rotate = res.data.rotate 等
      // 由于文档未明确返回格式，这里模拟加法（实际应以后端返回为准）
      arm.current.rotate += arm.adjust.rotate;
      arm.current.swing += arm.adjust.swing;
      arm.current.telescope += arm.adjust.telescope;

      // 清空本次调整值
      arm.adjust.rotate = 0;
      arm.adjust.swing = 0;
      arm.adjust.telescope = 0;
    } else {
      ElMessage.error(res?.msg || '微调失败');
    }
  } catch (err: any) {
    ElMessage.error(err?.message || '请求失败，请检查后端服务');
  }
};

// ========== 4. 批量微调 ==========
// 遍历所有机械臂，对每个有非零调整值的机械臂调用 sendSingleAdjust
// const sendBatchAdjust = async () => {
//   const tasks = armList.filter(arm =>
//       arm.adjust.rotate !== 0 || arm.adjust.swing !== 0 || arm.adjust.telescope !== 0
//   );

//   if (tasks.length === 0) {
//     ElMessage.warning('没有待下发的调整值');
//     return;
//   }

//   // 并行发送所有请求
//   const promises = tasks.map(arm => sendSingleAdjust(arm));
//   await Promise.all(promises);
//   ElMessage.success('批量微调指令已全部发送');
// };

// ========== 顶部功能按钮逻辑 ==========
const handleRosConnect = () => {
  ElMessage.success('已发送 ROS 重新连接请求...');
};

const handleSaveConfig = () => {
  // 这里以后可以替换成调用后端的保存接口
  console.log('当前保存的配置:', armList[0].current);
  ElMessage.success('机械臂当前姿态配置已成功保存到云端！');
};

const handleHistory = () => {
  ElMessage.info('历史记录面板即将上线，敬请期待...');
};

// ========== 5. 辅助功能 ==========
const resetAllAdjust = () => {
  armList.forEach(arm => {
    arm.adjust.rotate = 0;
    arm.adjust.swing = 0;
    arm.adjust.telescope = 0;
  });
  ElMessage.info('所有调整值已重置');
};

// 返回模块管理页面
const goBack = () => {
  router.push('/moduleManagement');
};

// ========== 6. 页面初始化 ==========
onMounted(() => {
  const qModuleId = route.query.module_id;
  const qDeviceId = route.query.device_id;

  if (qModuleId) {
    moduleId.value = parseInt(qModuleId as string);
  } else {
    ElMessage.warning('未获取到模块编号，请从模块管理页面进入');
  }

  if (qDeviceId) {
    currentDeviceId.value = parseInt(qDeviceId as string);
  }

  console.log('微调页面初始化完成', {
    module_id: moduleId.value,
    device_id: currentDeviceId.value
  });

  // 可选：页面加载时从后端获取所有机械臂的当前实际姿态值
  // 这里留空，待后端提供接口后可调用
});
</script>


<style scoped>

.fine-tuning-container {
  padding: 30px;
  background-color: #f0f2f5;
  height: calc(100vh - 150px);
  overflow: auto;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-button {
  font-size: 14px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.header-right {
  display: flex;
  gap: 10px;
}

/* ========== 卡片美化样式 ========== */
.arm-list {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.main-control-card {
  width: 750px; 
  border-radius: 12px;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05) !important;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-text {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.control-grid {
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 10px 20px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.label-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label-title {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.real-time-tag {
  font-size: 13px;
  color: #909399;
  background: #f4f4f5;
  padding: 4px 10px;
  border-radius: 4px;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 压力传感器黑盒样式 */
.sensor-panel {
  margin-top: 40px;
  background: #2b3243;
  border-radius: 8px;
  padding: 20px;
  color: #fff;
  text-align: center;
}

.sensor-title {
  font-size: 13px;
  color: #a8abb2;
  margin-bottom: 12px;
}

.sensor-value-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.value-text {
  font-size: 14px;
  letter-spacing: 1px;
}

/* 呼吸灯效果 */
.status-dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
}

.pulse {
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(245, 108, 108, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 108, 108, 0); }
}

.batch-bar {
  margin-top: 30px;
  display: flex;
  gap: 16px;
  justify-content: center;
}
</style>
