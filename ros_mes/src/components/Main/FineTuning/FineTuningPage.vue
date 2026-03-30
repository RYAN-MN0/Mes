<template>
  <div class="arm-adjust-container">
    <!-- 顶部导航区 -->
    <el-page-header content="机械臂姿态微调与压力监控">
      <template #extra>
        <el-tag :type="rosStatus ? 'success' : 'danger'">
          {{ rosStatus ? 'ROS已连接' : 'ROS断开连接' }}
        </el-tag>
        <el-button @click="saveConfig">保存配置</el-button>
        <el-button @click="resetConfig" type="warning">重置参数</el-button>
        <el-button @click="openHistory" type="primary">历史记录</el-button>
      </template>
    </el-page-header>

    <!-- 核心操作区：3台机械臂 -->
    <div class="arm-list">
      <div class="arm-item" v-for="(arm, index) in armList" :key="arm.id">
        <el-card :header="`机械臂${index+1}（编号：${arm.id}）`" shadow="hover">
          <!-- 硬件微调面板 -->
          <el-form :model="arm.hardware" label-width="auto">
            <!-- 底座旋转 -->
            <el-form-item label="底座旋转(°)" >
              <div class="adjust-group">
                <el-input-number 
                  v-model="arm.hardware.rotate.adjustValue" 
                  :min="0" :max="360" 
                  @change="updateAdjustValue(arm, 'rotate')">
                </el-input-number>
                <span class="current-value">当前值：{{ arm.hardware.rotate.currentValue }}°</span>
                <el-button size="small" @click="sendSingleArm(arm)" type="primary">下发微调</el-button>
              </div>
            </el-form-item>

            <!-- 中间摆动 -->
            <el-form-item label="中间摆动(°)">
              <div class="adjust-group">
                <el-input-number 
                  v-model="arm.hardware.swing.adjustValue" 
                  :min="-90" :max="90" 
                  @change="updateAdjustValue(arm, 'swing')">
                </el-input-number>
                <span class="current-value">当前值：{{ arm.hardware.swing.currentValue }}°</span>
                <el-button size="small" @click="sendSingleArm(arm)" type="primary">下发微调</el-button>
              </div>
            </el-form-item>

            <!-- 伸缩杆 -->
            <el-form-item label="伸缩杆(cm)">
              <div class="adjust-group">
                <el-input-number 
                  v-model="arm.hardware.telescope.adjustValue" 
                  :min="10" :max="50" 
                  :step="0.5"
                  @change="updateAdjustValue(arm, 'telescope')">
                </el-input-number>
                <span class="current-value">当前值：{{ arm.hardware.telescope.currentValue }}cm</span>
                <el-button size="small" @click="sendSingleArm(arm)" type="primary">下发微调</el-button>
              </div>
            </el-form-item>
          </el-form>

          <!-- 压力传感器 -->
          <div class="pressure-info">
            <el-tag :type="getPressureTagType(arm.pressure)">
              压力传感器：{{ arm.pressure }} N
            </el-tag>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 批量操作区 -->
    <div class="batch-operation">
      <el-input-number v-model="step" label="统一微调步长" :min="1" :max="10" style="width: 200px;"></el-input-number>
      <el-button type="primary" @click="sendBatchArm">批量下发所有微调</el-button>
      <el-button @click="syncPressure">同步压力值</el-button>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

// 基础数据定义
const rosStatus = ref(true) // ROS连接状态
const step = ref(5) // 统一微调步长
const historyVisible = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 机械臂数据（3台）
const armList = reactive([
  {
    id: 'ARM-001',
    hardware: {
      rotate: { currentValue: 150, adjustValue: 0 }, // 底座旋转
      swing: { currentValue: 30, adjustValue: 0 },    // 中间摆动
      telescope: { currentValue: 25, adjustValue: 0 } // 伸缩杆
    },
    pressure: 12.5 // 压力值(N)
  },
  {
    id: 'ARM-002',
    hardware: {
      rotate: { currentValue: 160, adjustValue: 0 },
      swing: { currentValue: 25, adjustValue: 0 },
      telescope: { currentValue: 24, adjustValue: 0 }
    },
    pressure: 15.2
  },
  {
    id: 'ARM-003',
    hardware: {
      rotate: { currentValue: 145, adjustValue: 0 },
      swing: { currentValue: 35, adjustValue: 0 },
      telescope: { currentValue: 26, adjustValue: 0 }
    },
    pressure: 18.8
  }
])

// 历史记录数据
const historyList = ref([])

// 压力均衡度计算
const balanceValue = computed(() => {
  const p1 = armList[0].pressure
  const p2 = armList[1].pressure
  const p3 = armList[2].pressure
  return Math.abs(p1 - p2) + Math.abs(p2 - p3) + Math.abs(p1 - p3)
})

const balanceDesc = computed(() => {
  const val = balanceValue.value
  if (val < 5) return '均衡（优）'
  if (val < 10) return '基本均衡（良）'
  return '不均衡（差）'
})

const balanceTips = computed(() => {
  const pressures = armList.map(item => item.pressure)
  const maxIndex = pressures.indexOf(Math.max(...pressures))
  return `建议微调机械臂${maxIndex+1}伸缩杆，降低压力值`
})

// 压力值标签类型
const getPressureTagType = (pressure) => {
  if (pressure < 10) return 'success'
  if (pressure < 20) return 'warning'
  return 'danger'
}

// 均衡度标签类型
const getBalanceTagType = () => {
  const val = balanceValue.value
  if (val < 5) return 'success'
  if (val < 10) return 'warning'
  return 'danger'
}

// 硬件数值微调
const adjustValue = (arm, type, val) => {
  arm.hardware[type].adjustValue += val
  // 限制范围
  if (type === 'rotate') {
    arm.hardware[type].adjustValue = Math.max(0, Math.min(360, arm.hardware[type].adjustValue))
  } else if (type === 'swing') {
    arm.hardware[type].adjustValue = Math.max(-90, Math.min(90, arm.hardware[type].adjustValue))
  } else if (type === 'telescope') {
    arm.hardware[type].adjustValue = Math.max(10, Math.min(50, arm.hardware[type].adjustValue))
  }
}

// 更新微调后的值（预览）
const updateAdjustValue = (arm, type) => {
  // 此处仅预览，实际下发后更新currentValue
}

// 单台机械臂下发微调
const sendSingleArm = async (arm) => {
  try {
    // 构造请求参数
    const params = {
      armId: arm.id,
      hardware: [
        { type: 'rotate', adjustValue: arm.hardware.rotate.adjustValue },
        { type: 'swing', adjustValue: arm.hardware.swing.adjustValue },
        { type: 'telescope', adjustValue: arm.hardware.telescope.adjustValue }
      ]
    }
    // 调用后端接口
    const res = await axios.post('/api/arm/adjust/single', params)
    if (res.data.code === 200) {
      ElMessage.success(`机械臂${arm.id}微调下发成功`)
      // 更新当前值和压力值
      arm.hardware.rotate.currentValue = res.data.data.rotate
      arm.hardware.swing.currentValue = res.data.data.swing
      arm.hardware.telescope.currentValue = res.data.data.telescope
      arm.pressure = res.data.data.pressure
      // 重置微调值
      arm.hardware.rotate.adjustValue = 0
      arm.hardware.swing.adjustValue = 0
      arm.hardware.telescope.adjustValue = 0
      // 更新图表
      updatePressureChart()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('下发失败：' + error.message)
  }
}

// 批量下发所有机械臂
const sendBatchArm = async () => {
  try {
    await ElMessageBox.confirm('确定批量下发所有机械臂微调参数？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // 构造请求参数
    const params = armList.map(arm => ({
      armId: arm.id,
      hardware: [
        { type: 'rotate', adjustValue: arm.hardware.rotate.adjustValue },
        { type: 'swing', adjustValue: arm.hardware.swing.adjustValue },
        { type: 'telescope', adjustValue: arm.hardware.telescope.adjustValue }
      ]
    }))
    // 调用后端接口
    const res = await axios.post('/api/arm/adjust/batch', params)
    if (res.data.code === 200) {
      ElMessage.success('批量下发成功')
      // 更新所有机械臂数据
      res.data.data.forEach(item => {
        const arm = armList.find(a => a.id === item.armId)
        if (arm) {
          arm.hardware.rotate.currentValue = item.rotate
          arm.hardware.swing.currentValue = item.swing
          arm.hardware.telescope.currentValue = item.telescope
          arm.pressure = item.pressure
          // 重置微调值
          arm.hardware.rotate.adjustValue = 0
          arm.hardware.swing.adjustValue = 0
          arm.hardware.telescope.adjustValue = 0
        }
      })
      // 更新图表
      updatePressureChart()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    if (error.message !== 'cancel') {
      ElMessage.error('批量下发失败：' + error.message)
    }
  }
}

// 同步压力值
const syncPressure = async () => {
  try {
    const res = await axios.get('/api/arm/pressure/sync')
    if (res.data.code === 200) {
      res.data.data.forEach(item => {
        const arm = armList.find(a => a.id === item.armId)
        if (arm) arm.pressure = item.pressure
      })
      ElMessage.success('压力值同步成功')
      updatePressureChart()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('同步失败：' + error.message)
  }
}

// 保存配置
const saveConfig = () => {
  ElMessage.success('配置已保存')
  // 实际项目中调用保存接口
}

// 重置参数
const resetConfig = () => {
  armList.forEach(arm => {
    arm.hardware.rotate.adjustValue = 0
    arm.hardware.swing.adjustValue = 0
    arm.hardware.telescope.adjustValue = 0
  })
  ElMessage.info('参数已重置')
}

// 打开历史记录
const openHistory = async () => {
  historyVisible.value = true
  // 调用历史记录接口
  try {
    const res = await axios.get('/api/arm/history', {
      params: { page: currentPage.value, size: pageSize.value }
    })
    historyList.value = res.data.data.list
    total.value = res.data.data.total
  } catch (error) {
    ElMessage.error('加载历史记录失败：' + error.message)
  }
}



</script>

<style scoped>
.arm-adjust-container {
  padding: 20px;
  background-color: #f5f7fa;
}

.arm-list {
  display: flex;
  gap: 20px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.arm-item {
  flex: 1;
  min-width: 440px;
}

.adjust-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.current-value {
  margin-left: 10px;
  color: #666;
}

.pressure-info {
  margin-top: 20px;
  padding: 10px;
  background-color: #f0f2f5;
  border-radius: 4px;
}

.batch-operation {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 20px 0;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
}

.monitor-area {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.balance-info {
  text-align: center;
  padding: 20px;
}

.balance-value {
  font-size: 32px;
  font-weight: bold;
  color: #1989fa;
  margin-bottom: 10px;
}

.balance-tips {
  margin-top: 10px;
  color: #666;
}
.el-form-item{
        max-width: 440px;
    margin: auto;
    margin-bottom: 18px;
}

</style>