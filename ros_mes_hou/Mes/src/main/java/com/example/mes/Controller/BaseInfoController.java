package com.example.mes.Controller;

import com.example.mes.Service.GetHardworkInfo;
import com.example.mes.pojo.Hardwork;
import com.example.mes.pojo.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;

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
        LocalDateTime createTime = LocalDateTime.now();
        LocalDateTime updateTime = LocalDateTime.now();
        Hardwork hardwork = new Hardwork(id, deviceName, type, spec, status, updateTime, createTime);
        getHardworkInfo.addHardwork(hardwork);
        return Result.success(200);
    }

    @GetMapping("/hardwork/select")
    public Result selectBySome(Hardwork hardwork){
        System.out.println(hardwork);
        hardwork.setId("%"+hardwork.getId()+"%");
        return Result.success(getHardworkInfo.selectBysome(hardwork));
    }


}