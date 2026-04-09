package com.example.mes.Controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.example.mes.ROS.Getdata;
import com.example.mes.Service.EmergencyStopService;
import com.example.mes.Service.ModuleService;
import com.example.mes.pojo.FineTuning;
import com.example.mes.pojo.FineTuningHistory;
import com.example.mes.pojo.Result;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;


@RestController
@CrossOrigin(origins = "*")
public class ModuleController {
    private ModuleService moduleservice;

    @PostMapping("/module/take")
    public Result takeStuff(@RequestBody FineTuning ft){
        String msg = "";
        try{
            FineTuningHistory data = moduleservice.sendFineTuning(ft);
            data.setDeviceId(ft.getDevice_id());
            data.setPosition(ft.getPosition());
            System.out.println((JSONObject) JSON.toJSON(data));
            return Result.success(data);
        } catch (Exception e) {
            msg = e.getMessage();
        }
        return Result.error(500,msg);
    }
}
