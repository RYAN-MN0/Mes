const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  devServer:{
    proxy:{
      '/api':{
        target:"http://192.168.0.117:8090",
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          '^/api': ""
        }
      }
    }
  }
})
