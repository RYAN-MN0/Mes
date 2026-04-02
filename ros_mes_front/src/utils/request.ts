import axios from "axios";
import qs from "qs";
import router from "@/router";
import { time } from "console";

const service = axios.create({
  baseURL: "/api", // 👈 必须写这个
  timeout: 10000,
  headers: {
    "Content-Type": "application/json;charset=utf-8",
  },
});

const timeLimit = 3*24*60*60*1000;

service.interceptors.request.use(
  function (config) {
    var token = localStorage.getItem("token");
    var nowtime = new Date();
    var updateToken = new Date(token.slice(12));
    var diffMs = Math.abs(nowtime.getTime() - updateToken.getTime());
    if (token && diffMs > 3) {
      router.push("/login");
    }
    // 自动转成 form 格式
    config.data = qs.stringify(config.data);
    // 设置请求头为表单格式
    config.headers["Content-Type"] = "application/x-www-form-urlencoded";
    
    return config;
  },
  function (error) {
    return Promise.reject(error);
  },
);

// 响应拦截
service.interceptors.response.use(
  (res) => res.data,
  (err) => Promise.reject(err)
)
export default service;
