import { defineStore } from "pinia";
import {ref} from "vue";

export const userStore = defineStore('user', () => {
    const userinfo = ref({
        account : '',
        password : '',
        token: '',
        updateToken: ''
    })

    const setUserInfo = (data: any) =>{
        userinfo.value = data
    }
    return { userinfo, setUserInfo }

})