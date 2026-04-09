package com.example.mes.Service;

import com.alibaba.fastjson.JSONObject;
import com.example.mes.ROS.Getdata;
import org.springframework.stereotype.Service;

@Service
public class EmergencyStopService {
    public JSONObject onstop() throws Exception {
        return Getdata.getClient().sendEmergencyStop();
    }
}
