package com.example.mes.ROS;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.example.mes.pojo.FineTuning;
import com.example.mes.pojo.FineTuningHistory;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Getdata extends WebSocketClient {

    private static final String ROS_URL = "ws://192.168.148.90:8765";
    private static Getdata clientInstance;
    private final ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();

    // ===================== 同步返回核心 =====================
    private ConcurrentHashMap<String, CompletableFuture<JSONObject>> futureMap = new ConcurrentHashMap<>();
    private ConcurrentHashMap<String, List<JSONObject>> moduleMsgCache = new ConcurrentHashMap<>();
    private ConcurrentHashMap<String, CompletableFuture<FineTuningHistory>> moduleFutureMap = new ConcurrentHashMap<>();

    public Getdata(URI serverUri) {
        super(serverUri);
        clientInstance = this;
    }

    public static Getdata getClient() {
        return clientInstance;
    }

    @Override
    public void onOpen(ServerHandshake handshakedata) {
        System.out.println("✅ 已连接 ROS");
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

    @Override
    public void onMessage(String message) {
        System.out.println("\n📥 收到ROS消息：" + message);
        try {
            JSONObject rosJson = JSON.parseObject(message);
            String msgId = rosJson.getString("msgId");

            // 1. 无msgId的消息直接丢弃
            if (msgId == null) return;

            // 2. 判断是否是module相关消息（msgId包含"module"字符串）
            if (msgId.contains("module")) {
                // 2.1 把当前消息存入对应msgId的缓存列表
                moduleMsgCache.computeIfAbsent(msgId, k -> new ArrayList<>()).add(rosJson);
                List<JSONObject> cachedList = moduleMsgCache.get(msgId);

                // 2.2 检查是否攒够3条消息
                if (cachedList.size() >= 3) {
                    // 2.3 3条消息攒齐，封装成FineTuningHistory
                    FineTuningHistory history = buildHistoryFromMsgList(cachedList);

                    // 2.4 从等待器Map中取出对应future，唤醒线程
                    CompletableFuture<FineTuningHistory> future = moduleFutureMap.get(msgId);
                    if (future != null) {
                        future.complete(history);
                        moduleFutureMap.remove(msgId); // 用完删除
                    }

                    // 2.5 清理缓存
                    moduleMsgCache.remove(msgId);
                }
            }
            // 3. 普通消息：直接走原有逻辑，唤醒线程
            else if (futureMap.containsKey(msgId)) {
                CompletableFuture<JSONObject> future = futureMap.get(msgId);
                future.complete(rosJson);
                futureMap.remove(msgId);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    private FineTuningHistory buildHistoryFromMsgList(List<JSONObject> msgList) {
        FineTuningHistory history = new FineTuningHistory();

        // 第1条：基础信息（moduleId、deviceId、position）
        JSONObject msg1 = msgList.get(0);
        history.setId(msg1.getInteger("id"));
        history.setModuleId(msg1.getString("moduleId"));

        // 第2-3条：传感器数据，合并成List
        List<Integer> sensorList = new ArrayList<>();
        for (int i = 1; i < msgList.size(); i++) {
            JSONObject msg = msgList.get(i);
            sensorList.add(msg.getInteger("sensorNum"));
        }
        history.setSensorNum(sensorList);

        return history;
    }
    // 发送指令，并等待ROS返回
    public JSONObject sendAndWait(JSONObject msg, long timeout, TimeUnit unit) throws Exception {
        if (!isOpen()) {
            throw new Exception("WebSocket未连接");
        }

        String msgId = System.currentTimeMillis() + "";
        msg.put("msgId", msgId);
        CompletableFuture<JSONObject> future = new CompletableFuture<>();
        futureMap.put(msgId, future);

        send(msg.toJSONString());
        System.out.println("✅ 已发送：" + msg);

        return future.get(timeout, unit);
    }

    public CompletableFuture<FineTuningHistory> sendModuleMsgAndWait(JSONObject msg, long timeout, TimeUnit unit) {
        if (!isOpen()) {
            throw new RuntimeException("WebSocket未连接");
        }

        String msgId = System.currentTimeMillis() + "_module"; // 确保msgId包含module
        msg.put("msgId", msgId);

        // 初始化缓存和等待器
        moduleMsgCache.put(msgId, new ArrayList<>());
        CompletableFuture<FineTuningHistory> future = new CompletableFuture<>();
        moduleFutureMap.put(msgId, future);

        // 发送消息
        send(msg.toJSONString());
        System.out.println("✅ 已发送module请求：" + msg);

        // 设置超时，避免无限等待
        future.completeOnTimeout(null, timeout, unit);
        return future;
    }


    // ===================== 业务方法：安全急停 =====================
    public JSONObject sendEmergencyStop() throws Exception {
        JSONObject msg = new JSONObject();
        msg.put("cmd", "STOP");
        msg.put("status", 0);
        return sendAndWait(msg, 3, TimeUnit.SECONDS);
    }

    // ===================== 重连 =====================
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