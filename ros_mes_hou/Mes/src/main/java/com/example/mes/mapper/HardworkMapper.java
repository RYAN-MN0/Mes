package com.example.mes.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import com.example.mes.pojo.Hardwork;

import java.util.List;

@Mapper
public interface HardworkMapper {
    public List<Hardwork> selectAll();

    public int add(Hardwork hardwork);

    public int deleteById(String id);

    public List<Hardwork> selectBySome(Hardwork hardwork);
}
