<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <div class="card-header">
        <p class="title">{{ isLogin ? '系统登录' : '新用户注册' }}</p>
      </div>

      <el-form 
        v-if="isLogin" 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="formRules" 
        label-width="0"
      >
        <el-form-item prop="username" label="账号" label-width="auto">
          <el-input v-model="loginForm.username" placeholder="请输入操作员账号" prefix-icon="User" clearable />
        </el-form-item>
        
        <el-form-item prop="password" label="密码" label-width="auto">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="submit-btn" @click="handleLogin" :loading="loading">登 录</el-button>
        </el-form-item>
        
        <div class="toggle-action">
          <el-link type="info" :underline="false" @click="isLogin = true">没有账号？申请注册</el-link>
        </div>
      </el-form>

      <el-form 
        v-else 
        ref="registerFormRef" 
        :model="registerForm" 
        :rules="formRules" 
        label-width="0"
      >
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" placeholder="设置操作员账号" prefix-icon="User" clearable />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="设置高强度密码" prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="再次确认密码" prefix-icon="Lock" show-password />
        </el-form-item>

        <el-alert title="注意：注册后需管理员审核通过方可登录" type="warning" show-icon :closable="false" class="audit-alert" />

        <el-form-item>
          <el-button type="success" class="submit-btn" @click="handleRegister" :loading="loading">提交注册申请</el-button>
        </el-form-item>
        
        <div class="toggle-action">
          <el-link type="info" :underline="false" @click="isLogin = true">返回登录</el-link>
        </div>
      </el-form>

    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus' // 引入消息提示组件

// 1. 状态控制
const isLogin = ref(true) // true为登录页，false为注册页
const loading = ref(false) // 按钮的加载转圈状态

// 2. 获取表单的 DOM 引用（为了触发校验）
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 3. 数据绑定容器
const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 4. 自定义高级校验规则：检查两次密码是否一致
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码以确认'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致！'))
  } else {
    callback() // 校验通过必须调用无参的 callback()
  }
}

// 5. 核心校验规则字典 (与 prop 属性一一对应)
const formRules = reactive({
  username: [
    { required: true, message: '操作员账号不能为空', trigger: 'blur' },
    { min: 3, max: 15, message: '账号长度需在 3 到 15 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度需在 6 到 20 个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
})

// 6. 登录按钮点击事件
const handleLogin = async () => {
  // 触发整表校验
  await loginFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      // TODO: 在这里接入 MD5 加密库处理 loginForm.password
      // TODO: 在这里调用 Java 后端 Axios 接口
      
      console.log('准备发送给后端的登录数据:', loginForm)
      
      // 模拟网络请求延迟
      setTimeout(() => {
        loading.value = false
        ElMessage.success('登录成功！即将跳转大屏...')
        // 注意：后续这里要处理 "密码错误3次锁定" 的后端状态码拦截
      }, 1000)
    } else {
      ElMessage.error('表单填写有误，请检查红字提示')
    }
  })
}

// 7. 注册按钮点击事件
const handleRegister = async () => {
  await registerFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      // TODO: MD5 加密处理
      console.log('准备发送给后端的注册数据:', registerForm)
      
      setTimeout(() => {
        loading.value = false
        ElMessage.success('申请提交成功！请等待管理员审核。')
        // 注册成功后自动切回登录界面，并清空注册表单
        registerFormRef.value.resetFields()
        isLogin.value = true 
      }, 1000)
    }
  })
}
</script>

<style scoped>
/* 背景铺满，深色工业风 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1f2430 0%, #2b3243 100%);
}

/* 卡片样式强化 */
.login-card {
  width: 420px;
  border-radius: 12px;
  border: 1px solid #3d4556;
  background-color: #ffffff;
  padding: 10px 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.sys-title {
  margin: 0;
  font-size: 22px;
  color: #303133;
  font-weight: 600;
  letter-spacing: 1px;
}

.sub-title {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.submit-btn {
  width: 100%;
  font-size: 16px;
  letter-spacing: 4px;
  margin-top: 10px;
}

.toggle-action {
  text-align: center;
  margin-top: 15px;
}

.audit-alert {
  margin-bottom: 20px;
}
</style>
```
