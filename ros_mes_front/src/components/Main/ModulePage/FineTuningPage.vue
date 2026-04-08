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
      <div class="header-right">
        <el-button type="primary">ROS连接</el-button>
        <el-button type="success">保存配置</el-button>
        <el-button type="warning">重置参数</el-button>
        <el-button type="info">历史记录</el-button>
      </div>
    </div>

    <!-- ========== 1. 当前操作信息展示 ========== -->
    <el-alert
        title="当前操作上下文"
        :description="`模块编号: ${moduleId} | 选中的机械臂: ${currentDeviceIdHex}`"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
    />

    <!-- ========== 2. 三个机械臂的微调面板 ========== -->
    <div class="arm-list">
      <el-card
          v-for="arm in armList"
          :key="arm.id"
          :header="`机械臂 ${arm.idHex}`"
          shadow="hover"
          class="arm-card"
      >
        <el-form label-width="100px">
          <!-- 旋转轴 -->
          <el-form-item label="旋转轴调整值(°)">
            <el-input-number
                v-model="arm.adjust.rotate"
                :min="-360" :max="360"
                placeholder="顺时针为正"
            />
            <span class="current-value">当前实际值: {{ arm.current.rotate }}°</span>
          </el-form-item>

          <!-- 摆动轴 -->
          <el-form-item label="摆动轴调整值(°)">
            <el-input-number
                v-model="arm.adjust.swing"
                :min="-90" :max="90"
            />
            <span class="current-value">当前实际值: {{ arm.current.swing }}°</span>
          </el-form-item>

          <!-- 伸缩杆 -->
          <el-form-item label="伸缩杆调整值(cm)">
            <el-input-number
                v-model="arm.adjust.telescope"
                :min="-20" :max="20"
                :step="0.5"
            />
            <span class="current-value">当前实际值: {{ arm.current.telescope }}cm</span>
          </el-form-item>

          <!-- 单个机械臂下发按钮 -->
          <el-form-item>
            <el-button type="primary" @click="sendSingleAdjust(arm)">下发微调</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- ========== 3. 批量操作栏 ========== -->
    <div class="batch-bar">
      <el-button type="success" @click="sendBatchAdjust">批量下发所有机械臂</el-button>
      <el-button @click="resetAllAdjust">重置所有调整值</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';

const router = useRouter();

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
  {
    id: 0x40,
    idHex: '0x40',
    adjust: { rotate: 0, swing: 0, telescope: 0 },
    current: { rotate: 160, swing: 25, telescope: 24 },
  },
  {
    id: 0x60,
    idHex: '0x60',
    adjust: { rotate: 0, swing: 0, telescope: 0 },
    current: { rotate: 145, swing: 35, telescope: 26 },
  },
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
const sendBatchAdjust = async () => {
  const tasks = armList.filter(arm =>
      arm.adjust.rotate !== 0 || arm.adjust.swing !== 0 || arm.adjust.telescope !== 0
  );

  if (tasks.length === 0) {
    ElMessage.warning('没有待下发的调整值');
    return;
  }

  // 并行发送所有请求
  const promises = tasks.map(arm => sendSingleAdjust(arm));
  await Promise.all(promises);
  ElMessage.success('批量微调指令已全部发送');
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
/* 样式略，与之前一致，保证布局整洁 */
.fine-tuning-container {
  padding: 20px;
  background-color: #fff;
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
.arm-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.arm-card {
  flex: 1;
  min-width: 380px;
}
.current-value {
  margin-left: 12px;
  font-size: 12px;
  color: #666;
}
.batch-bar {
  margin-top: 24px;
  display: flex;
  gap: 16px;
  justify-content: center;
}
.el-form-item {
  margin-bottom: 18px;
}
</style>