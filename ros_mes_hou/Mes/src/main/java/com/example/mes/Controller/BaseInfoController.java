package com.example.mes.Controller;

import com.example.mes.Service.GetHardwareInfo;
import com.example.mes.pojo.Hardware;
import com.example.mes.pojo.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;

@RestController
@CrossOrigin(origins = "*")
public class BaseInfoController {

    @Autowired
    private GetHardwareInfo GetHardwareInfo;

    @GetMapping("/hardwork")
    public Result selectall(){
        return Result.success(GetHardwareInfo.selectall());
    }

    @PutMapping("/hardwork")
    public Result addNewItem(String id, String deviceName, Integer type, String spec, Integer status) {
        Date createTime = new Date();
        Date updateTime = new Date();
        Hardware hardware = new Hardware(id, deviceName, type, spec, status, updateTime, createTime);
        GetHardwareInfo.addHardwork(hardware);
        return Result.success(GetHardwareInfo.selectall());
    }

    @GetMapping("/hardwork/select")
    public Result selectBySome(Hardware hardware){
        System.out.println(hardware);
        hardware.setId("%"+ hardware.getId()+"%");
        return Result.success(GetHardwareInfo.selectBysome(hardware));
    }

    @DeleteMapping("/hardwork")
    public Result deleteById(String id){
        String msg = GetHardwareInfo.deleteById(id);
        if(msg == "success"){
            return Result.success();
        }else{
            return Result.error(500,msg);
        }
    }




}