package com.example.mes.mapper;

import org.apache.ibatis.annotations.Mapper;
import com.example.mes.pojo.Hardware;

import java.util.List;

@Mapper
public interface HardwareMapper {
    public List<Hardware> selectAll();

    public int add(Hardware hardware);

    public int deleteById(String id);

    public List<Hardware> selectBySome(Hardware hardware);
}
