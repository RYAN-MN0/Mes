package com.example.mes.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Update;
import com.example.mes.pojo.User;

@Mapper
public interface Usermapper {
    public User selectAccount(String account, String password);

    public Integer insertAccount(User userinfo);

    public Integer updateToken (User userinfo);
}
