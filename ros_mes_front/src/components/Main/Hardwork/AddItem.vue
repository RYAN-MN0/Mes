<template>
  <el-drawer
    v-model="drawerVisible"
    title="添加硬件信息"
    :before-close="handleClose"
    direction="ltr"
    class="demo-drawer"
    style="min-width:300px"
  >
    <div class="demo-drawer__content">
      <el-form :model="form">
        <el-form-item label="硬件编号" :label-width="formLabelWidth">
          <el-input v-model="form.id" autocomplete="off" />
        </el-form-item>
        <el-form-item label="硬件名称" :label-width="formLabelWidth">
          <el-input v-model="form.deviceName" autocomplete="off" />
        </el-form-item>
        <el-form-item label="硬件类型" :label-width="formLabelWidth">
          <el-select v-model="form.type" placeholder="请选择硬件类型">
            <el-option v-for="value in typeOption" :key="value.id" :label="value.label" :value="value.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="硬件规格" :label-width="formLabelWidth">
          <el-input v-model="form.spec" autocomplete="off" />
        </el-form-item>
        <el-form-item label="硬件状态" prop="status" :label-width="formLabelWidth">
          <el-select-v2
            v-model="form.status"
            placeholder="请选择硬件状态"
            :options="options"
          />
        </el-form-item>
      </el-form>
      <div class="demo-drawer__footer">
        <el-button @click="cancelForm">取消</el-button>
        <el-button type="primary" :loading="loading" @click="onClick">
          {{ loading ? "正在提交 ..." : "提交" }}
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessageBox } from "element-plus";
import { computed } from "vue";
import request from "@/utils/request";

const props = defineProps({
  dialog: Boolean,
});
const emit = defineEmits(["update:dialog","update:hardworks"]);
const typeOption = [
  { id: "1", label: "机械臂" },
  { id: "2", label: "压力传感器" },
];
const drawerVisible = computed({
  get() {
    return props.dialog;
  },
  set(value) {
    emit("update:dialog", value);
  },
});
const formLabelWidth = "80px";
let timer: any;

const table = ref(false);
const loading = ref(false);

const form = reactive({
  id: "",
  deviceName: "",
  type: "",
  spec: "",
  status: "",
  updateTime: "",
  createTime: "",
});

const onClick = async () => {
  loading.value = true;
    try{
      var res = await request.put("/hardwork", {
      id: form.id,
      deviceName: form.deviceName,  
      type: form.type,
      spec: form.spec,
      status: form.status,
    });
    }catch(err){
      ElMessageBox.alert("添加失败,服务器未开启", "提示", {
        confirmButtonText: "确定"
      });
      loading.value = false;
      return;
    }
    if (res.code === 200) {
      ElMessageBox.alert("添加成功", "提示", {
        confirmButtonText: "确定",
      });
      res = await request.get("/hardwork");
      emit("update:dialog", false);
      emit("update:hardworks", res.data);
    } else {
      ElMessageBox.alert("添加失败," + res.msg, "提示", {
        confirmButtonText: "确定"
      });
    }
    loading.value = false;
};

const handleClose = (done:any) => {
  if (loading.value) {
    return;
  }
  ElMessageBox.confirm("是否提交?")
    .then(() => {
      loading.value = true;
      timer = setTimeout(() => {
        done();
        setTimeout(() => {
          loading.value = false;
          drawerVisible.value = false;
        }, 400);
      }, 2000);
    })
    .catch(() => {
      done();
      drawerVisible.value = false;
    });
};

const cancelForm = () => {
  loading.value = false;
  drawerVisible.value = false;
  clearTimeout(timer);
};

const options = Array.from({ length: 2 }).map((_, idx) => ({
  value: `${idx}`,
  label: `${idx === 0 ? "正常" : "故障"}`,
}));
</script>


