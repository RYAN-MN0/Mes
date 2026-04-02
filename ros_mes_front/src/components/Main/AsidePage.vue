<!-- eslint-disable -->
<template>
  <el-row class="tac" style="display:block">
    <el-col :span="12" style="max-width:100%">
      <el-menu
        default-active="1"
        class="el-menu-vertical-demo"
        @open="handleOpen"
        @close="handleClose"
        background-color="#d7e3fd"
      >
        <el-menu-item index="1">
          <el-icon><icon-menu /></el-icon>
          <span>硬件信息管理</span>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon><document /></el-icon>
          <span>模块管理</span>
        </el-menu-item>
        <el-menu-item index="3">
          <el-icon><setting /></el-icon>
          <span>微调模块</span>
        </el-menu-item>
      </el-menu>
    </el-col>
  </el-row>
</template>

<script  setup>
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'

const handleOpen = (key, keyPath) => {
  console.log(key, keyPath)
}
const handleClose = (key, keyPath) => {
  console.log(key, keyPath)
}
</script>