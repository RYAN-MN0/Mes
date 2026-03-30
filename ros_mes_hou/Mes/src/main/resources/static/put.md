## User 相当于数据格式吧
package pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
private String account;
private String password;
private String token;
private LocalDateTime updateToken;
}

## Result 当前端调用后返回的结果
package pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result {
private Integer code;
private String msg;
private Object data;

    public static Result success(){
        Result result = new Result();
        result.code = 1;
        result.msg = "OK";
        return result;
    }
    
    public static Result success(Object data){
        Result result = new Result();
        result.code = 1;
        result.msg = "OK";
        result.data = data;
        return result;
    }

    public static Result error(String msg){
        Result result = new Result();
        result.code = 0;
        result.msg = msg;
        return result;
    }
}

## Usermapper 从数据库拿数据的类
package com.example.mes.login;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojo.User;

@Mapper
public interface Usermapper {
@Select("select account,password from userinfo where account = #{account} and password = #{password}")
public User selectAccount(String account, String password);

    @Insert("insert into userinfo(account, password, token, updateToken) values(#{account},#{password},#{token},#{updateToken})")
    public void insertaccount(User userinfo);
}


## login 写接口供前端调用
package com.example.mes.login;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import pojo.Result;
import pojo.User;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;

@RestController
public class login {
@Autowired
private Usermapper usermapper;
@PutMapping("/user")
public Result insert(@RequestParam("account") String account, @RequestParam("password") String password){
System.out.println("1111");
User user = usermapper.selectAccount(account,password);
if(user == null){
return Result.error("账号密码错误");
}
return Result.success("登录成功");
}

}

## aplication.yaml 项目配置，包含连接数据库的信息
spring:
application:
name: Mes
datasource:
driver-class-name: com.mysql.cj.jdbc.Driver
url: jdbc:mysql://localhost:3306/mes
username: root
password: 123456

server:
port: 8090
address: 0.0.0.0
mybatis:
configuration:
#    匹配驼峰法与下划线法的命名方式
    map-underscore-to-camel-case: true
#    开启Mybatics日志输出
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
#  XML映射配置文件的路径
#  mapper-locations: classpath:mapper/*.xml

