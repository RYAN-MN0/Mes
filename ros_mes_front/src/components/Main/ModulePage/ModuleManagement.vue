<template>
  <div class="module-management">
    <div class="outer-table">
      <div class="title">模块管理与姿态调度</div>

      <!-- 操作栏：显示选中模块 + 设备选择 + 功能按钮 -->
      <!-- <div class="action-bar">
        <div class="module-info">
          <span class="info-label">当前选中模块：</span>
          <span class="info-value">({{ selectedCell.x }}, {{ selectedCell.y }})</span>
          <span class="info-label" style="margin-left: 20px;">模块编号：</span>
          <span class="info-value">{{ currentModuleId }}</span>
        </div>
        <div class="action-buttons">
          <div class="input-group device-select">
            <label>设备编号</label>
            <el-select v-model="deviceId" placeholder="选择机械臂" style="width: 140px;">
              <el-option label="当前坐标设备 (0)" :value="0" />
              <el-option label="机械臂1 (0x20)" :value="0x20" />
              <el-option label="机械臂2 (0x40)" :value="0x40" />
              <el-option label="机械臂3 (0x60)" :value="0x60" />
            </el-select>
          </div>
          <el-button type="primary" @click="openTargetDialog">设定目标位置</el-button>
          <el-button type="success" @click="handleFineTuning">姿态微调</el-button>
        </div>
      </div> -->
      <div class="action-bar-restored">
        <div class="input-row">
          <div class="input-group">
            <span class="prefix">X 坐标 (前四位)</span>
            <el-input v-model="inputX" class="binary-input" maxlength="4" @change="handleXChange" />
          </div>
          <div class="input-group">
            <span class="prefix">Y 坐标 (后四位)</span>
            <el-input v-model="inputY" class="binary-input" maxlength="4" @change="handleYChange" />
          </div>
          <el-button type="primary" class="lock-btn" @click="handleLockAndJump">锁定并下发</el-button>
        </div>
        <div class="hint-text">
          系统锁定目标: X(十进制 <span class="highlight">{{ selectedCell.x }}</span>) - Y(十进制 <span class="highlight">{{ selectedCell.y }}</span>)
        </div>
      </div>

      <!-- 8x8 模块矩阵 -->
      <div class="matrix-container">
        <div class="matrix">
          <div v-for="(row, yIndex) in matrix" :key="yIndex" class="matrix-row">
            <div
                v-for="cell in row"
                :key="`${cell.x}-${cell.y}`"
                class="matrix-cell"
                :class="{ selected: selectedCell.x === cell.x && selectedCell.y === cell.y }"
                @click="handleCellClick(cell)"
            >
              ({{ cell.x }},{{ cell.y }})
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 目标位置设定弹窗 -->
    <el-dialog
        v-model="dialogVisible"
        title="设定目标位置"
        width="400px"
        :close-on-click-modal="false"
        :close-on-press-escape="!loading"
        @close="handleDialogClose"
    >
      <el-form :model="targetForm" label-width="80px">
        <el-form-item label="X 坐标" required>
          <el-input-number
              v-model="targetForm.x"
              :min="-1000"
              :max="1000"
              :step="10"
              controls-position="right"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Y 坐标" required>
          <el-input-number
              v-model="targetForm.y"
              :min="-1000"
              :max="1000"
              :step="10"
              controls-position="right"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Z 坐标" required>
          <el-input-number
              v-model="targetForm.z"
              :min="-1000"
              :max="1000"
              :step="10"
              controls-position="right"
              style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false" :disabled="loading">取消</el-button>
          <el-button type="primary" @click="submitTargetMove" :loading="loading">
            {{ loading ? '正在移动中...' : '确定' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { useRouter } from 'vue-router';

const router = useRouter();

// 坐标与设备选择
const xCoord = ref(1);
const yCoord = ref(1);
const deviceId = ref(0);          // 0: 当前坐标设备, 0x20, 0x40, 0x60

// 矩阵数据 (8x8)
const matrixSize = 8;
const matrix = ref<any[]>([]);
const selectedCell = ref({ x: 1, y: 1 });

// 目标位置弹窗相关状态
const dialogVisible = ref(false);
const loading = ref(false);
const targetForm = ref({
  x: 0,
  y: 0,
  z: 0,
});

// 初始化矩阵
for (let y = 1; y <= matrixSize; y++) {
  const row = [];
  for (let x = 1; x <= matrixSize; x++) {
    row.push({ x, y });
  }
  matrix.value.push(row);
}

// 模块编号生成规则: x,y (1-15) -> 4位二进制拼接
const xyToModuleId = (x: number, y: number): number => {
  const xBin = (x - 1).toString(2).padStart(4, '0');
  const yBin = (y - 1).toString(2).padStart(4, '0');
  return parseInt(xBin + yBin, 2);
};

const currentModuleId = computed(() => xyToModuleId(selectedCell.value.x, selectedCell.value.y));


// ========== 替换刚才的 computed，使用更稳定的输入监听逻辑 ==========
// 1. 定义独立的输入框绑定值，不会再随便弹回去了
const inputX = ref('0001');
const inputY = ref('0001');

// 2. 监听下方矩阵点击：一旦格子变化，更新上方输入框
watch(selectedCell, (newVal) => {
  inputX.value = newVal.x.toString(2).padStart(4, '0');
  inputY.value = newVal.y.toString(2).padStart(4, '0');
}, { deep: true, immediate: true });

// 3. 监听 X 输入框的回车或失去焦点事件
// const handleXChange = (val: string) => {
//   const parsed = parseInt(val, 2);
//   // 校验：必须是数字，且在 1~8 的合法范围内
//   if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
//     selectedCell.value.x = parsed;
//     xCoord.value = parsed;
//     // 自动补齐为 4 位格式 (比如你只输入 10，自动变成 0010)
//     inputX.value = parsed.toString(2).padStart(4, '0');
//   } else {
//     // 如果输入乱码或超出范围，弹窗提示，并恢复当前选中格子的值
//     ElMessage.warning('请输入有效的四位二进制数 (例如: 0001 到 1000)');
//     inputX.value = selectedCell.value.x.toString(2).padStart(4, '0');
//   }
// };

// 4. 监听 Y 输入框的回车或失去焦点事件
// const handleYChange = (val: string) => {
//   const parsed = parseInt(val, 2);
//   if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
//     selectedCell.value.y = parsed;
//     yCoord.value = parsed;
//     inputY.value = parsed.toString(2).padStart(4, '0');
//   } else {
//     ElMessage.warning('请输入有效的四位二进制数 (例如: 0001 到 1000)');
//     inputY.value = selectedCell.value.y.toString(2).padStart(4, '0');
//   }
// };






// 3. 监听 X 输入框的事件
const handleXChange = (val: string) => {
  const parsed = parseInt(val, 2);
  if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
    // 【修复】不要用 selectedCell.value.x = parsed; 而是创建一个新对象
    selectedCell.value = { x: parsed, y: selectedCell.value.y };
    xCoord.value = parsed;
    inputX.value = parsed.toString(2).padStart(4, '0');
  } else {
    ElMessage.warning('请输入有效的四位二进制数 (例如: 0001 到 1000)');
    inputX.value = selectedCell.value.x.toString(2).padStart(4, '0');
  }
};

// 4. 监听 Y 输入框的事件
const handleYChange = (val: string) => {
  const parsed = parseInt(val, 2);
  if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
    // 【修复】创建一个新对象
    selectedCell.value = { x: selectedCell.value.x, y: parsed };
    yCoord.value = parsed;
    inputY.value = parsed.toString(2).padStart(4, '0');
  } else {
    ElMessage.warning('请输入有效的四位二进制数 (例如: 0001 到 1000)');
    inputY.value = selectedCell.value.y.toString(2).padStart(4, '0');
  }
};

// 点击矩阵格子（【修复】赋值为一个新对象，防止后续操作污染矩阵原数据）
const handleCellClick = (cell: any) => {
  selectedCell.value = { x: cell.x, y: cell.y }; 
  xCoord.value = cell.x;
  yCoord.value = cell.y;
};


// 点击矩阵格子
// const handleCellClick = (cell: any) => {
//   selectedCell.value = cell;
//   // 同步坐标输入框（供其他逻辑使用）
//   xCoord.value = cell.x;
//   yCoord.value = cell.y;
// };

// ========== 锁定并下发：跳转到微调页面 ==========
const handleLockAndJump = () => {
  const module_id = currentModuleId.value;
  
  if (module_id === undefined || module_id === null) {
    ElMessage.warning('未能获取到有效的模块编号');
    return;
  }

  // 携带计算好的 module_id 跳转到微调页面
  router.push({
    path: '/FineTuningPage',
    query: {
      module_id: module_id.toString()
    }
  });
};



// 打开目标位置弹窗，重置表单
const openTargetDialog = () => {
  targetForm.value = { x: 0, y: 0, z: 0 };
  dialogVisible.value = true;
};

// 关闭弹窗时的清理
const handleDialogClose = () => {
  if (!loading.value) {
    dialogVisible.value = false;
  }
};

// 提交目标位置：调用后端接口，等待ROS到达后关闭弹窗
const submitTargetMove = async () => {
  const { x, y, z } = targetForm.value;
  // 校验坐标是否均为有效数字（InputNumber 已保证是数字，但做兜底）
  if (isNaN(x) || isNaN(y) || isNaN(z)) {
    ElMessage.error('请填写有效的 X、Y、Z 坐标');
    return;
  }

  const module_id = currentModuleId.value;
  const position = [x, y, z];

  // 校验设备编号（若需限制具体机械臂可在此提示，但接口允许0代表当前坐标设备）
  if (deviceId.value === undefined || deviceId.value === null) {
    ElMessage.error('请选择有效的机械臂编号');
    return;
  }

  console.log('下发目标位置参数:', { module_id, device_id: deviceId.value, position });

  loading.value = true;
  try {
    // 调用后端目标下发接口，后端会等待 ROS 执行完毕并返回结果
    const res = await request.put('/module/put', {
      module_id,
      device_id: deviceId.value,
      position,
    });

    if (res && res.code === 200) {
      ElMessage.success(`模块 ${module_id} 已成功到达目标位置 (${x}, ${y}, ${z})`);
      // 成功到达后关闭弹窗
      dialogVisible.value = false;
    } else {
      ElMessage.error(res?.msg || '目标位置下发失败，请重试');
    }
  } catch (err: any) {
    console.error('目标位置下发异常:', err);
    ElMessage.error(err?.message || '请求失败，请检查后端服务');
  } finally {
    loading.value = false;
  }
};

// 姿态微调：跳转至微调页面，进行精细调节
const handleFineTuning = async () => {
  const module_id = currentModuleId.value;
  // 建议选择具体的机械臂进行微调，避免使用“当前坐标设备(0)”
  if (deviceId.value === 0) {
    ElMessage.warning('微调操作需要选择具体的机械臂（0x20 / 0x40 / 0x60），请重新选择');
    return;
  }
  console.log('跳转微调页面，参数:', { module_id, device_id: deviceId.value });
  await router.push({
    path: '/FineTuningPage',
    query: {
      module_id: module_id.toString(),
      device_id: deviceId.value.toString()
    }
  });
};


</script>

<style scoped>
.module-management {
  padding: 20px;
  background-color: #ffffff;
  border-radius: 10px;
  height: calc(100vh - 150px);
  overflow: auto;
}
.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}
/* 新的操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}
.module-info {
  font-size: 14px;
  color: #333;
}
.info-label {
  font-weight: 500;
  color: #606266;
}
.info-value {
  font-weight: bold;
  color: #409eff;
  margin-right: 8px;
}
.action-buttons {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}
.device-select {
  display: flex;
  align-items: center;
  gap: 10px;
}
.device-select label {
  font-weight: 500;
  color: #606266;
}
.matrix-container {
  display: flex;
  justify-content: center;
  overflow-x: auto;
}
.matrix {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 10px;
  background-color: #ffffff;
  display: inline-block;
}
.matrix-row {
  display: flex;
  gap: 5px;
  margin-bottom: 5px;
}
.matrix-cell {
  width: 70px;
  height: 50px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  background-color: #f5f7fa;
  transition: all 0.2s ease;
}
.matrix-cell:hover {
  background-color: #ecf5ff;
  transform: translateY(-2px);
}
.matrix-cell.selected {
  background-color: #409eff;
  color: #fff;
  font-weight: bold;
}


/* 新增的还原截图样式 */
/* 新增的还原截图样式 (精修版) */
.action-bar-restored {
  background-color: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  border-left: 4px solid #409eff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); /* 增加轻微阴影，更有质感 */
  display: flex;
  flex-direction: column;
  align-items: center; /* 内部元素居中 */
  gap: 12px;
  width: fit-content;  /* 拒绝拉伸，宽度由内容撑开 */
  margin-left: auto;
  margin-right: auto;  /* 整个面板整体居中 */
}

.input-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.input-group {
  display: flex;
  align-items: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
  height: 36px; /* 降低整体高度，更秀气 */
}

.prefix {
  padding: 0 12px;
  color: #606266;
  font-size: 13px;
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
  line-height: 36px;
  white-space: nowrap; /* 防止文字换行 */
}

.binary-input :deep(.el-input__wrapper) {
  box-shadow: none !important;
  width: 70px; /* 缩窄输入框，只需放4位数字 */
  padding: 0;
}

/* 让二进制数字居中并使用等宽字体，更像极客面板 */
.binary-input :deep(.el-input__inner) {
  text-align: center;
  font-family: monospace;
  font-size: 15px;
  letter-spacing: 1px;
}

.lock-btn {
  height: 36px;
  padding: 0 20px;
}

.hint-text {
  font-size: 13px;
  color: #909399;
}

.hint-text .highlight {
  color: #409eff;
  font-weight: bold;
  font-size: 14px;
}
</style>