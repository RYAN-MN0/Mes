package com.example.mes.ROS;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import com.alibaba.fastjson.JSONObject;
import java.net.URI;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Getdata extends WebSocketClient {

    // 改成你的 ROS 虚拟机 IP
    private static final String ROS_URL = "ws://192.168.148.90:8765";
    private static Getdata clientInstance;
    private final ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();

    public Getdata(URI serverUri) {
        super(serverUri);
        clientInstance = this;
    }

    // 获取单例（方便全局发送消息）
    public static Getdata getClient() {
        return clientInstance;
    }

    @Override
    public void onOpen(ServerHandshake handshakedata) {
        System.out.println("✅ 已连接 ROS");
    }

    // 接收 ROS 消息（含 header）
    @Override
    public void onMessage(String message) {
        System.out.println("\n📥 收到ROS消息：" + message);
//        try {
//            JSONObject data = JSONObject.parseObject(message);
//            String name = data.getString("name");
//            int age = data.getInteger("age");
//            double height = data.getDouble("height");
//            boolean isStudent = data.getBoolean("is_student");
//
//            JSONObject header = data.getJSONObject("header");
//            String frameId = header.getString("frame_id");
//            JSONObject stamp = header.getJSONObject("stamp");
//            long secs = stamp.getLong("secs");
//            long nsecs = stamp.getLong("nsecs");
//
//            System.out.println("姓名：" + name);
//            System.out.println("年龄：" + age);
//            System.out.println("身高：" + height);
//            System.out.println("是否学生：" + isStudent);
//            System.out.println("frame_id：" + frameId);
//            System.out.println("时间戳：" + secs + "." + nsecs);
//        } catch (Exception e) {
//            System.out.println("ROS回复：" + message);
//        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        System.out.println("❌ 断开，30秒后重连...");
        retry();
    }

    @Override
    public void onError(Exception ex) {
        System.out.println("⚠️ 连接异常，30秒后重连...");
        retry();
    }

    // 发送消息给 ROS（核心方法！）
    public void sendToRos(String msg) {
        if (isOpen()) {
            send(msg);
            System.out.println("✅ 已发送给ROS：" + msg);
        } else {
            System.out.println("❌ 未连接，发送失败");
        }
    }

    private void retry() {
        executor.schedule(() -> {
            try {
                reconnectBlocking();
            } catch (Exception ignored) {}
        }, 30, TimeUnit.SECONDS);
    }

    public static void start() {
        try {
            new Getdata(URI.create(ROS_URL)).connectBlocking();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}