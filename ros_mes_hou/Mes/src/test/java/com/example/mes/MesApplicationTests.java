package com.example.mes;

import com.example.mes.ROS.Getdata;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class MesApplicationTests {
    public static void main(String[] args){
        // 发送字符串
        Getdata.getClient().sendToRos("start_arm");

        // 发送 JSON 指令（机械臂控制）
        Getdata.getClient().sendToRos("{\"action\":\"move\",\"speed\":0.5}");
    }

    @Test
    void contextLoads() {
    }


}
