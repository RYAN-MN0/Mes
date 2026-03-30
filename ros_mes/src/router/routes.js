// jjj
const routes = [
    {
        name:'main',
        path:'/',
        component: ()=>import('../components/Main/MainPage.vue'),
        meta:{preFetch: true}
    },
    {
        name:'login',
        path:'/login',
        component: ()=>import('../components/Login/login.vue'),
        meta:{preFetch: true}
    }
]
export default routes