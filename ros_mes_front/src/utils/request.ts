import axios from "axios";
import qs from "qs";
import router from "@/router";
import { ElMessage } from "element-plus";

const service = axios.create({
  baseURL: "/api", // 👈 必须写这个
  timeout: 10000,
  headers: {
    "Content-Type": "application/json;charset=utf-8",
  },
});

const timeLimit = 3 * 24 * 60 * 60 * 1000;// 3天

service.interceptors.request.use(
  function (config) {
    // 自动转成 form 格式
    // config.data = qs.stringify(config.data);
    // 设置请求头为表单格式
    // config.headers["Content-Type"] = "application/x-www-form-urlencoded";


      // 登录接口除外，其他都需要 token 校验
    if (config.url != "/user") {
        const  token = localStorage.getItem("token");
        const updateTime = localStorage.getItem("updateTime");

      if (!token || !updateTime) {
        ElMessage.error("请先登录");
        router.replace("/login");
        return Promise.reject(new Error("请先登录"));
      }

      // var nowtime = new Date();
      // var updateToken = new Date(token.slice(12));
      // var diffMs = Math.abs(nowtime.getTime() - updateToken.getTime());
      // if (diffMs > timeLimit) {
      //   router.push("/login");
      //   ElMessage.error("Token过期，请重新登录");
      //   router.replace("/login");
      //   return Promise.reject(new Error("Token过期，请重新登录"));
      // }

        const now = Date.now();
        const last = new Date(updateTime).getTime();
        if (now - last > timeLimit) {
            ElMessage.error("Token过期，请重新登录");
            router.replace("/login");
            return Promise.reject(new Error("Token过期"));
        }

        // 添加 token 到请求头
        config.headers["Authorization"] = `Bearer ${token}`
    }

    return config;
  },
  function (error) {
    return Promise.reject(error);
  },
);

 // 响应拦截器：统一处理 401
service.interceptors.response.use(
  (res) => res.data,
  (err) => {
      if (err.response?.status === 401) {
          localStorage.removeItem("token");
          localStorage.removeItem("updateTime");
          router.replace("/login");
          ElMessage.error("未授权，请重新登录");
      }
      return Promise.reject(err);
  }
);
export default service;
