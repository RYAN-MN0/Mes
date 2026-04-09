package com.example.mes.Service;

import com.example.mes.mapper.HardwareMapper;
import com.example.mes.pojo.Hardware;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class GetHardwareInfo {
    @Autowired
    private HardwareMapper hardwareMapper;

    public List<Hardware> selectall(){
        List<Hardware> hardwares = hardwareMapper.selectAll();
        return hardwares;
    }

    public void addHardwork(Hardware hardware) {
        if (hardware.getId() == null || hardware.getId().isEmpty()) {
            throw new RuntimeException("设备ID不能为空");
        }
        hardwareMapper.add(hardware);
    }

    public List<Hardware> selectBysome(Hardware hardware){
        return hardwareMapper.selectBySome(hardware);
    }
    public String deleteById(String id){
        Integer rows = hardwareMapper.deleteById(id);
        System.out.println(rows);
        if(rows < 1){
            return "该机械编号不存在！";
        }
        return "success";
    }
}
