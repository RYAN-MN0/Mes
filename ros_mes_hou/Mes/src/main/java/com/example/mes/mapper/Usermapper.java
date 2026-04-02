package com.example.mes.mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import com.example.mes.pojo.User;

@Mapper
public interface Usermapper {
    @Select("select account,password,token,updateToken from userinfo where account = #{account} and password = #{password}")
    public User selectAccount(String account, String password);

    @Insert("insert into userinfo(account, password, token, updateToken) values(#{account},#{password},#{token},#{updateToken})")
    public void insertaccount(User userinfo);

    @Update("update userinfo set token = #{token}, updateToken = #{updateToken} where account = #{account}")
    public int updatetoken (User userinfo);
}
