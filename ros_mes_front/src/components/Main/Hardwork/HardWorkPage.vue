<template>
  <div class="container">
    <!-- 搜索表单 -->
    <el-form :model="searchForm" label-width="80px" style="max-width: 600px">
      <el-form-item label="硬件编号">
        <el-input v-model="searchForm.id" placeholder="请输入硬件编号" clearable />
      </el-form-item>
      <el-form-item label="硬件类型">
        <el-select v-model="searchForm.type" placeholder="请选择类型" clearable>
          <el-option label="机械臂" :value="1" />
          <el-option label="压力传感器" :value="2" />
          <!-- 可根据实际扩展 -->
        </el-select>
      </el-form-item>
      <el-form-item label="规格">
        <el-input v-model="searchForm.spec" placeholder="请输入规格" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button type="success" @click="openAddDialog">+ 新增硬件</el-button>
      </el-form-item>
    </el-form>

    <!-- 硬件列表表格 -->
    <el-table :data="hardworks" border stripe style="width: 100%">
      <el-table-column prop="id" label="硬件编号" width="150" />
      <el-table-column prop="deviceName" label="硬件名称" width="150" />
      <el-table-column prop="type" label="硬件类型" width="120">
        <template #default="{ row }">
          {{ row.type === 1 ? "机械臂" : "压力传感器" }}
        </template>
      </el-table-column>
      <el-table-column prop="spec" label="规格" width="150" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? "正常" : "故障" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updateTime" label="最近使用时间" width="180" />
      <el-table-column prop="createTime" label="创建时间" width="180" />
      <el-table-column fixed="right" label="操作" width="120">
        <template #default="{ row }">
          <el-button link type="danger" size="small" @click="deleteRow(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增硬件弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增硬件" width="500px">
      <el-form :model="addForm" :rules="addFormRules" ref="addFormRef" label-width="100px">
        <el-form-item label="硬件编号" prop="id">
          <el-input v-model="addForm.id" placeholder="唯一标识，不可重复" />
        </el-form-item>
        <el-form-item label="硬件名称" prop="deviceName">
          <el-input v-model="addForm.deviceName" />
        </el-form-item>
        <el-form-item label="硬件类型" prop="type">
          <el-select v-model="addForm.type" placeholder="请选择类型">
            <el-option label="机械臂" :value="1" />
            <el-option label="压力传感器" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格" prop="spec">
          <el-input v-model="addForm.spec" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="addForm.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">故障</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">确认新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, FormInstance, FormRules } from "element-plus";
import request from "@/utils/request";

// ---------- 类型定义 ----------
interface Hardware {
  id: string;
  deviceName: string;
  type: number;    // 1=机械臂, 2=压力传感器
  spec: string;
  status: number;  // 1=正常, 0=故障
  updateTime: string;
  createTime: string;
}

// ---------- 模拟数据 ----------
const mockHardworks: Hardware[] = [
  {
    id: "HW001",
    deviceName: "机械臂A",
    type: 1,
    spec: "负载5kg",
    status: 1,
    updateTime: "2024-01-01 10:00:00",
    createTime: "2023-12-01 08:00:00",
  },
  {
    id: "HW002",
    deviceName: "压力传感器B",
    type: 2,
    spec: "精度0.1mm",
    status: 0,
    updateTime: "2024-01-02 11:00:00",
    createTime: "2023-12-02 09:00:00",
  },
  {
    id: "HW003",
    deviceName: "机械臂C",
    type: 1,
    spec: "负载10kg",
    status: 1,
    updateTime: "2024-01-03 12:00:00",
    createTime: "2023-12-03 10:00:00",
  },
];

// 表格数据
const hardworks = ref<Hardware[]>([]);

// 搜索表单
const searchForm = reactive({
  id: "",
  type: null as number | null,
  spec: "",
});

// 新增弹窗相关
const addDialogVisible = ref(false);
const addFormRef = ref<FormInstance>();
const addForm = reactive<Hardware>({
  id: "",
  deviceName: "",
  type: 1,
  spec: "",
  status: 1,
  updateTime: "",
  createTime: "",
});

// 新增表单校验规则（包含 id 唯一性校验）
const addFormRules: FormRules = {
  id: [
    { required: true, message: "请输入硬件编号", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        const exists = hardworks.value.some(item => item.id === value);
        if (exists) {
          callback(new Error("硬件编号已存在"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
  deviceName: [{ required: true, message: "请输入硬件名称", trigger: "blur" }],
  type: [{ required: true, message: "请选择硬件类型", trigger: "change" }],
  spec: [{ required: true, message: "请输入规格", trigger: "blur" }],
};

// ---------- 模拟数据操作函数 ----------
const loadMockData = () => {
  hardworks.value = [...mockHardworks];
};

// 模拟搜索
const searchMock = () => {
  let filtered = [...mockHardworks];
  if (searchForm.id) {
    filtered = filtered.filter(item => item.id.includes(searchForm.id));
  }
  if (searchForm.type !== null && searchForm.type !== undefined) {
    filtered = filtered.filter(item => item.type === searchForm.type);
  }
  if (searchForm.spec) {
    filtered = filtered.filter(item => item.spec.includes(searchForm.spec));
  }
  hardworks.value = filtered;
};

// 模拟新增
const addMock = (newHardware: Hardware) => {
  mockHardworks.push(newHardware);
  hardworks.value.push(newHardware);
  ElMessage.success("添加成功");
};

// 模拟删除
const deleteMock = (row: Hardware) => {
  const index = mockHardworks.findIndex(item => item.id === row.id);
  if (index !== -1) mockHardworks.splice(index, 1);
  const idx = hardworks.value.findIndex(item => item.id === row.id);
  if (idx !== -1) hardworks.value.splice(idx, 1);
  ElMessage.success("删除成功");
};

// ---------- 真实接口（注释保留，后续切换）----------
/*
// 全量查询
const loadFromApi = () => {
  request.get("/hardwork").then((res) => {
    hardworks.value = res;
  }).catch(err => {
    ElMessage.error("获取硬件列表失败");
  });
};

// 模糊搜索
const searchFromApi = () => {
  request.get("/hardwork/select", {
    params: {
      id: searchForm.id || undefined,
      type: searchForm.type ?? undefined,
      spec: searchForm.spec || undefined,
    }
  }).then((res) => {
    hardworks.value = res;
  }).catch(err => {
    ElMessage.error("搜索失败");
  });
};

// 新增硬件
const addToApi = (data: Hardware) => {
  request.put("/hardwork", data).then(() => {
    ElMessage.success("添加成功");
    addDialogVisible.value = false;
    loadFromApi(); // 刷新列表
  }).catch(err => {
    if (err.response?.status === 400) {
      ElMessage.error("硬件编号已存在");
    } else {
      ElMessage.error("添加失败");
    }
  });
};

// 删除硬件（如果后端支持）
const deleteFromApi = (id: string) => {
  request.delete("/hardwork", { params: { id } }).then(() => {
    ElMessage.success("删除成功");
    loadFromApi();
  }).catch(err => {
    ElMessage.error("删除失败");
  });
};
*/

// ---------- 事件处理（当前使用模拟数据）----------
const handleSearch = () => {
  searchMock();     // 模拟搜索
  // searchFromApi(); // 真实接口（需要时取消注释）
};

const openAddDialog = () => {
  addForm.id = "";
  addForm.deviceName = "";
  addForm.type = 1;
  addForm.spec = "";
  addForm.status = 1;
  addDialogVisible.value = true;
};

const submitAdd = async () => {
  await addFormRef.value?.validate();
  const now = new Date().toISOString().replace("T", " ").substring(0, 19);
  const newHardware: Hardware = {
    ...addForm,
    updateTime: now,
    createTime: now,
  };
  addMock(newHardware);     // 模拟新增
  // addToApi(newHardware);  // 真实接口（需要时取消注释）
  addDialogVisible.value = false;
};

const deleteRow = async (row: Hardware) => {
  ElMessageBox.confirm("确定删除该硬件吗？", "提示", { type: "warning" }).then(() => {
    deleteMock(row);        // 模拟删除
    // deleteFromApi(row.id); // 真实接口（需要时取消注释）
  }).catch(() => {});
};

onMounted(() => {
  loadMockData();   // 加载模拟数据
  // loadFromApi();  // 真实接口（需要时取消注释）
});
</script>

<style scoped>
.container {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 10px;
  height: calc(100vh - 150px);
  display: flex;
  flex-direction: column;
  overflow: auto;
}
.container > :last-child {
  flex: 1;
}
</style>