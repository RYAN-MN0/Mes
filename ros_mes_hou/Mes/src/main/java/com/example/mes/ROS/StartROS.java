package com.example.mes.ROS;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class StartROS implements CommandLineRunner {
    @Override
    public void run(String... args) throws Exception {
        Getdata.start();
        Thread.sleep(1000);
    }
}