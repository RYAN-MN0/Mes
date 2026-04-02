package com.example.mes.Controller;

import com.example.mes.Service.GetHardworkInfo;
import com.example.mes.pojo.Hardwork;
import com.example.mes.pojo.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;

@RestController
public class BaseInfoController {

    @Autowired
    private GetHardworkInfo getHardworkInfo;

    @GetMapping("/hardwork")
    public Result selectall(){
        return Result.success(getHardworkInfo.selectall());
    }

    @PutMapping("/hardwork")
    public Result addNewItem(String id, String deviceName, Integer type, String spec, Integer status) {
        Date createTime = new Date();
        Date updateTime = new Date();
        Hardwork hardwork = new Hardwork(id, deviceName, type, spec, status, updateTime, createTime);
        getHardworkInfo.addHardwork(hardwork);
        return Result.success(getHardworkInfo.selectall());
    }

    @GetMapping("/hardwork/select")
    public Result selectBySome(Hardwork hardwork){
        System.out.println(hardwork);
        hardwork.setId("%"+hardwork.getId()+"%");
        return Result.success(getHardworkInfo.selectBysome(hardwork));
    }

    @DeleteMapping("/hardwork")
    public Result deleteById(String id){
        String msg = getHardworkInfo.deleteById(id);
        if(msg == "success"){
            return Result.success();
        }else{
            return Result.error(500,msg);
        }
    }




}