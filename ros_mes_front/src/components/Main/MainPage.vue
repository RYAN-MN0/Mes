<template>
  <div class="common-layout" style="height:100%">
    <el-container style="height:100%">
      <!-- <el-container>
        <Aside></Aside>
        <el-container>
          <el-main style="background-color: #f5f7fa; padding: 20px; height:100%; overflow:scroll">
            <div>
              <Head></Head>
             <HardWorkPage></HardWorkPage>
              <FineTuningPage></FineTuningPage>
              <router-view></router-view>
            </div>
          </el-main>
        </el-container>
      </el-container> -->


       <el-aside :width="layoutStore.fold ? '64px' : '220px'" style="transition: width 0.3s ease;"><Aside></Aside></el-aside>

      <el-container>
        <el-header><Head></Head></el-header>
        <el-main><router-view></router-view></el-main>
      </el-container>
    </el-container>
  </div>
</template>


<script lang="ts" setup>
import Aside from '../Main/AsidePage.vue';
import FineTuningPage from '../Main/ModulePage/FineTuningPage.vue';
import HardWorkPage from '../Main/Hardwork/HardWorkPage.vue';
import Head from  '../Head/head.vue'
import { useLayoutSettingStore } from '@/stores/layoutSetting';


const layoutStore = useLayoutSettingStore();
</script>

<style>
.common-layout{
  height: 100%;
  width: 100%;
  background-color: #ffff;
}
.common-layout .el-container{
  background-color: #eff5f4;
  height: 100%;
}
.common-layout .el-header {
  padding: 0;
  /* margin: 0; */
  height: 60px;
}
</style>