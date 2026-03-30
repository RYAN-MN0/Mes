package com.example.mes.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import pojo.Hardwork;

import java.util.List;

@Mapper
public interface Hardworkmapper {
    @Select("select id,device_name,type,spec,status,update_time,create_time from hardwork")
    public List<Hardwork> selectAll();

    @Select("select id,device_name,type,spec,status,update_time,create_time from hardwork where id Like '%#{text}%' or device_name Like '%#{text}%';")
    public List<Hardwork> selectid(String text);
}
