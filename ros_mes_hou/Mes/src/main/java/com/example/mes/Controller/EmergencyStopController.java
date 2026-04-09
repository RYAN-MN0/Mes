package com.example.mes.Controller;

import com.alibaba.fastjson.JSONObject;
import com.example.mes.Service.EmergencyStopService;
import com.example.mes.pojo.Result;
import lombok.AllArgsConstructor;
import lombok.Data;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin("*")
public class EmergencyStopController {
    private EmergencyStopService emergencyStopService;

    @PostMapping("/stop")
    public Result onstop(@RequestBody Integer status){
        String msg = "";
        try{
            JSONObject data = emergencyStopService.onstop();
            return Result.success(data);
        } catch (Exception e) {
            msg = e.getMessage();
        }
        return Result.error(500,msg);
    }
}
