<template>
    <button v-on:click="search">search</button>
    <el-table :data="hardworks" style="max-width:1200px;margin:0 auto" max-height="900" max-width="800">
    <el-table-column fixed prop="id" label="硬件编号" width="150" />
    <el-table-column prop="deviceName" label="硬件名称" width="120" />
    <el-table-column prop="type" label="硬件类型" width="120" />
    <el-table-column prop="spec" label="规格" width="120" />
    <el-table-column prop="status" label="状态" width="120" />
    <el-table-column prop="updateTime" label="最近使用时间" width="120" />
    <el-table-column prop="createTime" label="创建时间" width="120"/>
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
</template>

<script setup>
import { ref } from 'vue'
import dayjs from 'dayjs'
import axios from 'axios'

const now = new Date({})

const hardworks = ref()
const deleteRow = (index) => {
  hardworks.value.splice(index, 1)
}

const onAddItem = () => {
  now.setDate(now.getDate() + 1)
  hardworks.value.push({
    date: dayjs(now).format('YYYY-MM-DD'),
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  })
}

const search = async()=>{
    try{
        const res = await axios.get("/api/hardwork")
        hardworks.value = res.data.data
        console.log(res.data,hardworks[0])
    }catch(err){
        console.error("请求失败",err)
    }
}


</script>
