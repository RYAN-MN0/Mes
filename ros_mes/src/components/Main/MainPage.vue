<template>
  <div class="common-layout" style="height:100%">
    <el-container>
      <el-header style="backgroundColor:#d7e3fd" height="80px">
        <Top></Top>
      </el-header>
      <el-container>
        <el-aside width="200px" >
          <Aside></Aside>
        </el-aside>
        <el-container>
          <el-main style="padding:0">
            <div>
              <!-- <HardWorkPage></HardWorkPage> -->
              <FineTuningPage></FineTuningPage>
            </div>
          </el-main>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>


<script>
import Top from './TopPage.vue'
import Aside from './AsidePage.vue'
import FineTuningPage from './FineTuning/FineTuningPage.vue';
import HardWorkPage from './Hardwork/HardWorkPage.vue';
// import { onMounted, onUnmounted, reactive } from 'vue';
export default {
  name: "MainPage",
  components:{
    Top, Aside, FineTuningPage, HardWorkPage
  },
  setup(){
    // let height = reactive(0)
    // function updateHeight() {
    //   height.value = window.innerHeight - 80
    // }
    // onMounted(()=>{
    //   updateHeight()
    //   window.addEventListener('resize',updateHeight)
    // })
    // onUnmounted(()=>{
    //   window.removeEventListener('resize',updateHeight)
    // })
    // return {
    //   height
    // }
  }
}
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