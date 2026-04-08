import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import {useUserStore} from "../stores/user";

const router = createRouter({
  history: createWebHistory(),
  routes
});


//添加路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  // 注意：页面刷新后 pinia 状态会丢失，需要从 localStorage 恢复，但我们在 setUserInfo 时已同步存入了 localStorage，
  // 而刷新后 pinia 会重新初始化，所以需要在 app 启动时恢复。这个我们下一步再做。
  // 现在先简单判断 localStorage 中的 token 是否有效
  const token = localStorage.getItem('token');
  const updateTime = localStorage.getItem('updateTime');

  let isValid = false;

  if (token && updateTime) {
    const now = Date.now();
    const last = new Date(updateTime).getTime();
    if (now - last <= 3 * 24 * 60 * 60 * 1000) {
      isValid = true;
    }
  }

  if (to.path !== '/login' && !isValid) {
    next('/login');
  } else {
    next();
  }
});

export default router