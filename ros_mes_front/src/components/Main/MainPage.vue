<template>
  <div class="common-layout" style="height:100%">
    <el-container style="height:100%">
      <el-container>
        <Aside></Aside>
        <el-container>
          <el-main style="background-color: #f5f7fa; padding: 20px; height:100%; overflow:scroll">
            <div>
              <HardWorkPage></HardWorkPage>
              <!-- <FineTuningPage></FineTuningPage> -->
            </div>
          </el-main>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>


<script lang="ts" setup>
import Aside from '@/components/Main/AsidePage.vue';
import FineTuningPage from '@/components/Main/ModulePage/FineTuningPage.vue';
import HardWorkPage from '@/components/Main/Hardwork/HardWorkPage.vue';


</script>

<style>
.top{
  position: fixed;
  width: 100%;
  background-color: #fff;
  z-index: 1000;
}
.main{
  position: relative;
  margin-top: 60px;
  z-index: 0;
}
ul{
  background-color: #d7e3fd;
}
</style>