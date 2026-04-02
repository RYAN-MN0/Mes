package com.example.mes.login;

import com.example.mes.mapper.Usermapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.example.mes.pojo.Result;
import com.example.mes.pojo.User;

import java.time.LocalDateTime;
import java.util.Random;

@RestController
public class login {
    @Autowired
    private Usermapper usermapper;
    @PutMapping("/user")
    public Result logging(String account, String password){
        User user = usermapper.selectAccount(account,password);
        if(user == null){
            return Result.error(400,"账号密码错误");
        }
        Random random = new Random();
        char [] token = new char[12];
        for(int i=0;i<12;i++){
            int index = random.nextInt(65,122);
            token[i] = (char) index;
        }
        user.setToken(new String(token));
        user.setUpdateToken(LocalDateTime.now());
        int rows = usermapper.updatetoken(user);
        if(rows < 0){
            return Result.error(400,"服务器错误，请重试");
        }
        return Result.success(user);
    }

}
