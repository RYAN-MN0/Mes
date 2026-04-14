#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import serial 
import threading
from std_msgs.msg import Header
from robot_control_backend.msg import Feedback, IntCmd

class STM32Bridge:
    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        # 串口初始化
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.running = True

        # 发布/订阅
        self.pub_feedback = rospy.Publisher("/hardware/all_feedback", Feedback, queue_size=10)
        rospy.Subscriber("/arm/cmd_vel", IntCmd, self.on_cmd_received)

        # 发送指令缓存（仅数据变化时发送）
        self.last_sent_data = None  

        # ===================== 核心配置 =====================
        self.START_MODULE_ID = 0x11          # 数据帧起始标识
        # 设备ID配置
        self.PRESSURE_SENSOR_ID = 49         # 压力传感器
        self.ENCODER_IDS = [41, 42, 43]      # 3个编码器
        # 数据长度配置
        self.PRESSURE_DATA_LEN = 6           # 压力传感器：6字节
        self.ENCODER_DATA_LEN = 4            # 编码器：4字节
        # 时间判定：1秒无新数据 → 判定数据传输完毕
        self.IDLE_TIMEOUT = 1.0  

        # 数据接收缓冲区（持续累积串口数据）
        self.serial_buffer = b""
        # 记录【最后一次收到串口数据的时间】（核心：用于空闲判定）
        self.last_data_receive_time = rospy.Time.now()

        # 启动独立线程：持续读取串口数据
        self.start_read_thread()
        # 启动ROS定时器：高频检查空闲状态（100ms检查一次，精准灵敏）
        self.timer = rospy.Timer(rospy.Duration(0.1), self.idle_detect_callback)

    # -------------------------------------------------------------------------
    # 发送逻辑：仅数据变化时发送指令
    # -------------------------------------------------------------------------
    def on_cmd_received(self, msg):
        module_id = msg.module_id
        device_id = msg.device_id
        pos_val = int(msg.position[0])

        current_data = (module_id, device_id, pos_val)
        if current_data != self.last_sent_data:
            data_high = (pos_val >> 8) & 0xFF
            data_low = pos_val & 0xFF
            send_bytes = bytes([module_id, device_id, data_high, data_low])
            self.ser.write(send_bytes)
            self.last_sent_data = current_data
            rospy.loginfo(f"[下发指令] %02X %02X %02X %02X", module_id, device_id, data_high, data_low)

    # -------------------------------------------------------------------------
    # 串口独立线程：持续读取数据 → 存入缓冲区 → 更新最后接收时间
    # -------------------------------------------------------------------------
    def read_serial_thread(self):
        while self.running and not rospy.is_shutdown():
            try:
                if self.ser.in_waiting > 0:
                    # 读取所有串口数据，追加到缓冲区
                    new_data = self.ser.read(self.ser.in_waiting)
                    self.serial_buffer += new_data
                    # 关键：收到新数据，刷新最后接收时间
                    self.last_data_receive_time = rospy.Time.now()
                    rospy.logdebug(f"[串口接收] 新增数据长度: {len(new_data)}, 总缓存: {len(self.serial_buffer)}")
            except Exception as e:
                rospy.logerr(f"串口读取异常: {str(e)}")
            rospy.sleep(0.001)

    # -------------------------------------------------------------------------
    # 1秒空闲检测回调（核心逻辑）
    # -------------------------------------------------------------------------
    def idle_detect_callback(self, event):
        # 计算空闲时间
        idle_time = (rospy.Time.now() - self.last_data_receive_time).to_sec()
        
        # --------------------- 核心判定 ---------------------
        if idle_time < self.IDLE_TIMEOUT:
            # 1秒内仍收到数据 → 下位机还在传输 → 跳过解析，继续等待
            return
        
        # --------------------- 1秒无数据 → 传输完毕 → 开始处理 ---------------------
        rospy.loginfo(f"===== 判定完成：{self.IDLE_TIMEOUT}秒无新数据，下位机传输结束，开始解析 =====")
        buffer = self.serial_buffer

        # 无数据直接清空返回
        if len(buffer) == 0:
            rospy.logwarn("[数据丢弃] 缓冲区为空，无有效数据")
            self.serial_buffer = b""
            return

        # 查找所有有效数据帧起始位置
        start_positions = [i for i, byte in enumerate(buffer) if byte == self.START_MODULE_ID]
        if not start_positions:
            rospy.logwarn("[数据丢弃] 未找到0x11起始标识，清空无效数据")
            self.serial_buffer = b""
            return

        # 遍历解析所有设备帧（支持4个设备同时上传）
        for start in start_positions:
            # 防止越界
            if start + 1 >= len(buffer):
                rospy.logwarn(f"[数据丢弃] 帧位置{start}数据不完整，跳过")
                continue

            device_id = buffer[start + 1]
            data_len = 0
            device_name = ""

            # 按device_id判断设备类型
            if device_id == self.PRESSURE_SENSOR_ID:
                data_len = self.PRESSURE_DATA_LEN
                device_name = "压力传感器"
            elif device_id in self.ENCODER_IDS:
                data_len = self.ENCODER_DATA_LEN
                device_name = f"编码器{device_id}"
            else:
                # ✅ 丢弃未知设备数据 + 打印日志
                rospy.logwarn(f"[数据丢弃] 未知设备ID:{device_id}，跳过该帧")
                continue

            # ✅ 数据不足 → 丢弃 + 打印日志
            if start + data_len > len(buffer):
                rospy.logwarn(f"[数据丢弃] {device_name}(ID:{device_id}) 数据长度不足，跳过")
                continue

            # 提取完整有效帧
            valid_frame = buffer[start:start+data_len]

            try:
                # 压力传感器：6字节 → 取第2-5字节（4字节）解析
                if device_id == self.PRESSURE_SENSOR_ID:
                    pressure_val = (valid_frame[2] << 24) | (valid_frame[3] << 16) | (valid_frame[4] << 8) | valid_frame[5]
                    position_val = pressure_val
                # 编码器：4字节 → 取第2-3字节解析
                else:
                    position_val = (valid_frame[2] << 8) | valid_frame[3]

                # 发布反馈数据
                msg = Feedback()
                msg.header = Header(stamp=rospy.Time.now())
                msg.module_id = valid_frame[0]
                msg.device_id = device_id
                msg.position = [position_val]
                self.pub_feedback.publish(msg)

                rospy.loginfo(f"[解析发布] {device_name} ID:{device_id} 数值:{position_val}")

            except Exception as e:
                rospy.logerr(f"[数据丢弃] 解析设备{device_id}失败: {str(e)}，跳过")
                continue

        # 解析完成 → 清空缓冲区
        self.serial_buffer = b""
        rospy.loginfo(f"===== 数据处理完成，缓冲区已清空，等待下一轮传输 =====")

    # -------------------------------------------------------------------------
    # 线程启动/关闭
    # -------------------------------------------------------------------------
    def start_read_thread(self):
        t = threading.Thread(target=self.read_serial_thread)
        t.daemon = True
        t.start()

    def close(self):
        self.running = False
        self.ser.close()

if __name__ == "__main__":
    rospy.init_node("stm32_bridge")
    bridge = STM32Bridge("/dev/ttyUSB0", 115200)
    rospy.loginfo(f"STM32联通节点启动成功 → {1}秒空闲判定传输结束")
    rospy.spin()
    bridge.close()