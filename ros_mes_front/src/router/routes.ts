import LoginPage from "../components/Login/LoginPage.vue";
import MainPage from "../components/Main/MainPage.vue";
import HardWorkPage from "../components/Main/Hardwork/HardWorkPage.vue";
import FineTuningPage from "../components/Main/ModulePage/FineTuningPage.vue";
import ModuleManagement from "../components/Main/ModulePage/ModuleManagement.vue";


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/',
    name: 'Main',
    component: MainPage,
    redirect: '/HardWorkPage',   // 默认显示硬件信息管理页面
    children: [
      { path: '/HardWorkPage', component: HardWorkPage },
      { path: '/ModuleManagement', component: ModuleManagement },
      { path: '/FineTuningPage', component: FineTuningPage },
    ]
  }
]


export default routes