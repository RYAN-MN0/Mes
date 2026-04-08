<template>
  <div class="module-management">
    <div class="outer-table">
      <div class="title">模块管理与姿态调度</div>

      <div class="coordinate-inputs">
        <div class="coordinate-input-container">
          <div class="input-group">
            <label>X坐标 (1-15)</label>
            <el-input-number v-model="xCoord" :min="1" :max="15" />
          </div>
          <div class="input-group">
            <label>Y坐标 (1-15)</label>
            <el-input-number v-model="yCoord" :min="1" :max="15" />
          </div>
          <div class="input-group">
            <label>目标位置 (X,Y,Z)</label>
            <el-input v-model="positionX" placeholder="X" style="width:70px" />
            <el-input v-model="positionY" placeholder="Y" style="width:70px" />
            <el-input v-model="positionZ" placeholder="Z" style="width:70px" />
          </div>
          <div class="input-group">
            <label>设备编号</label>
            <el-select v-model="deviceId" placeholder="选择机械臂">
              <el-option label="当前坐标设备 (0)" :value="0" />
              <el-option label="机械臂1 (0x20)" :value="0x20" />
              <el-option label="机械臂2 (0x40)" :value="0x40" />
              <el-option label="机械臂3 (0x60)" :value="0x60" />
            </el-select>
          </div>
          <el-button type="primary" @click="handleLockAndSend">锁定并下发</el-button>
        </div>
        <div class="system-target">
          <span>当前选中模块: ({{ selectedCell.x }}, {{ selectedCell.y }})</span>
          <span style="margin-left: 20px;">模块编号: {{ currentModuleId }}</span>
        </div>
      </div>

      <div class="matrix-container">
        <div class="matrix">
          <div v-for="(row, yIndex) in matrix" :key="yIndex" class="matrix-row">
            <div
                v-for="cell in row"
                :key="`${cell.x}-${cell.y}`"
                class="matrix-cell"
                :class="{ 'selected': selectedCell.x === cell.x && selectedCell.y === cell.y }"
                @click="handleCellClick(cell)"
            >
              ({{ cell.x }},{{ cell.y }})
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { useRouter } from 'vue-router';
const router = useRouter();

const xCoord = ref(1);
const yCoord = ref(1);
const positionX = ref('0');
const positionY = ref('0');
const positionZ = ref('0');
const deviceId = ref(0);

const matrixSize = 8;
const matrix = ref<any[]>([]);
const selectedCell = ref({ x: 1, y: 1 });

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

const handleCellClick = (cell: any) => {
  selectedCell.value = cell;
  // 可选：同步坐标输入框
  xCoord.value = cell.x;
  yCoord.value = cell.y;
};

const handleLockAndSend = async () => {
  const module_id = currentModuleId.value;
  const position = [Number(positionX.value), Number(positionY.value), Number(positionZ.value)];

  if (position.some(isNaN)) {
    ElMessage.error('目标位置必须为数字');
    return;
  }

  console.log('下发参数:', { module_id, device_id: deviceId.value, position });
      await router.push({
        path: '/FineTuningPage',
        query: {
          module_id: module_id.toString(),
          device_id: deviceId.value.toString()
        }
      });

  // 真实接口
  // try {
  //   const res = await request.put('/module/put', {
  //     module_id,
  //     device_id: deviceId.value,
  //     position
  //   });
  //   if (res && res.code === 200) {
  //     ElMessage.success('目标下发成功，即将跳转至微调页面');
  //     await router.push({
  //       path: '/FineTuningPage',
  //       query: {
  //         module_id: module_id.toString(),
  //         device_id: deviceId.value.toString()
  //       }
  //     });
  //   } else {
  //     ElMessage.error(res?.msg || '下发失败');
  //   }
  // } catch (err: any) {
  //   ElMessage.error(err?.message || '请求失败');
  // }
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
.coordinate-inputs {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 5px;
  margin-bottom: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  margin-top: 20px;
}
.coordinate-input-container {
  display: flex;
  gap: 20px;
  padding-left: 15px;
  margin-top: 15px;
  flex-wrap: wrap;
  align-items: center;
}
.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.system-target {
  margin-bottom: 15px;
  font-size: 14px;
  color: #409eff;
  padding-left: 15px;
}
.matrix-container {
  display: flex;
  justify-content: center;
  padding-left: 15px;
  margin-top: 20px;
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
</style>