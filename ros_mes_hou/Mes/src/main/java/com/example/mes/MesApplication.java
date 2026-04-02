package com.example.mes;

import com.example.mes.ROS.Getdata;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;


import java.net.URI;

@SpringBootApplication
public class MesApplication{
    public static void main(String[] args) {
//        Getdata.start();
        SpringApplication.run(MesApplication.class, args);
        // 发送字符串
//        Getdata.getClient().sendToRos("hello");

        // 发送 JSON 指令（机械臂控制）
//        Getdata.getClient().sendToRos("{\"action\":\"move\",\"speed\":0.5}");
    }
}

