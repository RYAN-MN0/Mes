<template>
  <div>
    <el-form
      ref="ruleFormRef"
      style="max-width: 600px"
      :model="ruleForm"
      :rules="rules"
      label-width="auto"
    >
      <el-form-item label="硬件名称" prop="id">
        <el-input v-model="ruleForm.id" placeholder="请输入硬件名称" />
      </el-form-item>
      <el-form-item label="硬件类型" prop="type">
        <el-input v-model="ruleForm.type" placeholder="请输入硬件类型" />
      </el-form-item>
      <el-form-item label="规格" prop="spec">
        <el-input v-model="ruleForm.spec" placeholder="请输入规格" />
      </el-form-item>
      <el-form-item label="createTime">
        <el-col :span="11">
          <el-form-item prop="date1">
            <el-date-picker
              v-model="ruleForm.date1"
              type="date"
              aria-label="Pick a date"
              placeholder="Pick a date"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col class="text-center" :span="2">
          <span class="text-gray-500">-</span>
        </el-col>
        <el-col :span="11">
          <el-form-item prop="date2">
            <el-time-picker
              v-model="ruleForm.date2"
              aria-label="Pick a time"
              placeholder="Pick a time"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-form-item>
          <el-button type="primary" @click="search">搜索</el-button>
        </el-form-item>
      </el-form-item>
    </el-form>
    <el-table
      :data="hardworks"
      style="max-width: 1200px; margin: 0 auto"
      max-height="900"
      max-width="800"
    >
      <el-table-column fixed prop="id" label="硬件编号" width="150" />
      <el-table-column prop="deviceName" label="硬件名称" width="120" />
      <el-table-column prop="type" label="硬件类型" width="120" />
      <el-table-column prop="spec" label="规格" width="120" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="updateTime" label="最近使用时间" width="120" />
      <el-table-column prop="createTime" label="创建时间" width="120" />
      <el-table-column fixed="right" label="操作" min-width="120">
        <template #default="scope">
          <el-button
            link
            type="primary"
            size="small"
            @click.prevent="deleteRow(scope.$index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- <el-button class="mt-4" style="max-width:1200px;margin:0 auto" @click="onAddItem">
    添加+
  </el-button> -->
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import request from '@/utils/request'
import type {FormInstance, FormRules } from 'element-plus'

interface RuleForm {
  id: string;
  type: string;
  date1: string;
  date2: string;
  spec: string;
}

const ruleFormRef = ref<FormInstance>()
const ruleForm = reactive<RuleForm>({
  id: "",
  type: "",
  date1: "",
  date2: "",
  spec: "",
})

const locationOptions = ['Home', 'Company', 'School']

const rules = reactive<FormRules<RuleForm>>({
  id: [
    {
      type: "string",
      message: "请输入硬件编号或硬件名称",
      trigger: "change",
    },
  ],
  spec: [
    {
      type: "array",
      message: "请输入硬件规格",
      trigger: "change",
    },
  ],
  date1: [
    {
      type: "date",
      message: "请输入起始时间",
      trigger: "change",
    },
  ],
  date2: [
    {
      type: "date",
      message: "请输入结束时间",
      trigger: "change",
    },
  ],
  type: [
    {
      type: "array",
      required: true,
      message: "Please select at least one activity type",
      trigger: "change",
    },
  ],
})

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      console.log('submit!')
    } else {
      console.log('error submit!', fields)
    }
  })
}

const options = Array.from({ length: 10000 }).map((_, idx) => ({
  value: `${idx + 1}`,
  label: `${idx + 1}`,
}))


const now = new Date();
const hardworks = ref();
const deleteRow = (index: number) => {
  hardworks.value.splice(index, 1);
};

const onAddItem = () => {
  now.setDate(now.getDate() + 1);
  hardworks.value.push({
    name: "Tom",
    state: "California",
    city: "Los Angeles",
    address: "No. 189, Grove St, Los Angeles",
    zip: "CA 90036",
  });
};

const search = async () => {
  try {
    const res = await axios.get("/hardwork");
    hardworks.value = res.data.data;
  } catch (err) {
    console.error("请求失败", err);
  }
};

onMounted(async () => {
  try {
    request.get("/hardwork").then((res) => {
      hardworks.value = res.data.data;
    });
  } catch (err) {
    console.error("请求失败", err);
  }
});
</script>