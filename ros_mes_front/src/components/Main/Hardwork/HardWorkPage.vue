<template>
  <div>
    <el-form
      ref="hardworksRef"
      style="max-width: 600px"
      :model="hardworks"
      label-width="auto"
    >
      <el-form-item label="硬件名称" prop="id">
        <el-input v-model="hardworkInfo.id" placeholder="请输入硬件名称" />
      </el-form-item>
      <el-form-item label="硬件规格" prop="type">
        <el-select v-model="hardworkInfo.type" placeholder="请选择类型">
          <el-option label="机械臂" value="1" />
          <el-option label="压力传感器" value="2" />
        </el-select>
      </el-form-item>
      <el-form-item label="规格" prop="spec">
        <el-input v-model="hardworkInfo.spec" placeholder="请输入规格" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary"  @click="open">添加</el-button>
        <el-button type="primary" @click="search">搜索</el-button>
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
            @click.prevent="deleteRow(scope)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <AddItem v-model:dialog="showdialog" @update:hardworks="(newval)=> hardworks=newval"></AddItem>
    <!-- <el-button class="mt-4" style="max-width:1200px;margin:0 auto" @click="onAddItem">
    添加+
  </el-button> -->
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from "vue";
import AddItem from "./AddItem.vue";
import request from "@/utils/request";
import { ElMessageBox } from "element-plus";

const showdialog = ref(false);
const hardworkInfo = reactive({
  id: "",
  type: "",
  spec: "",
});
const hardworks = ref([]);
const now = new Date();

const deleteRow = async (scope: any) => {
    console.log(scope.row.id)
    const res = await request.delete("/hardwork",{
        params: {
            id: scope.row.id,
        }
    })
    if (res.code === 200) {
      ElMessageBox.alert("删除成功", "提示", {
        confirmButtonText: "确定",
      });
      hardworks.value = hardworks.value.slice(scope.$index, 1);
    } else {
      ElMessageBox.alert("删除失败," + res.msg, "提示", {
        confirmButtonText: "确定",
      });
    }
};

const open = () => {
  showdialog.value = true;
  console.log(showdialog.value)
};


const search = async () => {
  try {
    const res = await request.get("/hardwork/select", {
      params: {
        id: hardworkInfo.id,
        type: hardworkInfo.type,
        spec: hardworkInfo.spec,
      },
    });
    hardworks.value = res.data;
  } catch (err) {
    console.error("请求失败", err);
  }
};

onMounted(async () => {
  try {
    request.get("/hardwork").then((res:any) => {
      hardworks.value = res.data;
    });
  } catch (err) {
    console.error("请求失败", err);
  }
});
</script>