package com.example.mes.Service;

import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson2.JSON;
import com.example.mes.ROS.Getdata;
import com.example.mes.pojo.FineTuning;
import com.example.mes.pojo.FineTuningHistory;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class ModuleService {
    public FineTuningHistory sendFineTuning(FineTuning ft) throws Exception {
        JSONObject js = (JSONObject) JSON.toJSON(ft);
        FineTuningHistory fth = Getdata.getClient().sendModuleMsgAndWait(js, 10, TimeUnit.SECONDS).get();
        return fth;
    }
}
