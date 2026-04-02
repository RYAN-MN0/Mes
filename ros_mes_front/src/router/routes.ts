import LoginPage from "../components/Login/LoginPage.vue";
import MainPage from "../components/Main/MainPage.vue";
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/',
    name: 'Main',
    component: MainPage
  }
]


export default routes