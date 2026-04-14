#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32  # 下位机收整数，无需引入Float32
from robot_control_backend.msg import SwingCmd, Feedback  # 导入统一反馈msg

## --------------------摆动轴功能节点----------------
class SwingSimple:
    def __init__(self):
        rospy.init_node("swing_simple_node")
        rospy.loginfo("✅ 摆动轴节点启动：已加入单位换算，适配双指令+统一反馈")

        # --- 核心参数配置 ---
        # 已知：1编码 = 0.01248°（与旋转轴一致，仅用于度转编码下发下位机）
        self.DEGREE_PER_TICK = 0.01248
        
        # 核心变量（与旋转轴节点规范统一）
        self.target_delta_deg = 0.0     # 指令给的：增量角度（度）
        self.current_swing_deg = 0.0    # 硬件反馈：当前实际角度（度，已由反馈节点转换）
        self.target_reach_deg = 0.0     # 最终要到达的角度 = 当前 + 增量

        # 订阅双指令话题（按要求订阅微调+运动学计算指令）
        # 1. 前端下发的摆动轴微调指令
        rospy.Subscriber("/control/adjust_swing_cmd", SwingCmd, self.cmd_callback)
        # 2. 运动计算节点发布的摆动轴运动命令
        rospy.Subscriber("/control/kinematics_swing_cmd", SwingCmd, self.cmd_callback)
        
        # 订阅统一硬件反馈：从/hardware/swing_feedback提取摆动轴角度（device_id=34，对应Feedback.msg定义）
        rospy.Subscriber("/hardware/swing_feedback", Feedback, self.feedback_callback)
        
        # 发布话题：发给联通节点、给到下位机的数据（Int32类型，符合要求）
        self.output_pub = rospy.Publisher("/hardware/swing_output", Int32, queue_size=10)

        self.rate = rospy.Rate(20)  # 20Hz控制频率，与旋转轴节点一致

    def cmd_callback(self, msg):
        """接收度为单位的增量指令（适配SwingCmd.msg float64[]格式），兼容双话题指令"""
        # 从SwingCmd的position数组提取第一个元素作为有效增量角度（与旋转轴指令格式统一）
        self.target_delta_deg = msg.position[0]
        # 区分指令来源（便于调试，明确是微调还是运动学计算指令）
        cmd_topic = msg._connection_header.get('topic', '未知话题')
        if cmd_topic == "/control/adjust_swing_cmd":
            rospy.loginfo(f"📥 收到摆动轴微调指令：+{self.target_delta_deg:.4f}°")
        elif cmd_topic == "/control/kinematics_swing_cmd":
            rospy.loginfo(f"📥 收到摆动轴运动学计算指令：+{self.target_delta_deg:.4f}°")

    def feedback_callback(self, msg):
        """从统一反馈中提取摆动轴角度（device_id=34，已由反馈节点完成编码→度转换）"""
        # 只处理摆动轴的反馈数据（严格匹配Feedback.msg的device_id定义：42=摆动轴编码器）
        if msg.device_id == 34:
            # 提取角度值（position数组第一个元素，单位：度，适配Feedback.msg float64[]格式）
            self.current_swing_deg = msg.position[0]
            # 计算最终目标角度（当前角度 + 指令增量角度）
            self.target_reach_deg = self.current_swing_deg + self.target_delta_deg
            # 调试日志：确认反馈数据正常接收（终端调试模式可查看）
            rospy.logdebug(f"📩 收到摆动轴反馈：当前角度{self.current_swing_deg:.2f}°")

    def run(self):
        while not rospy.is_shutdown():
            # --- 核心逻辑：角度 -> 编码值（适配下位机整数需求）---
            # 1. 计算原始浮点编码值
            raw_tick = self.target_reach_deg / self.DEGREE_PER_TICK
            # 2. 四舍五入取整（下位机只认整数，必须转换）
            target_tick = int(round(raw_tick))
            # 3. 发布给下位机（Int32类型，符合要求）
            self.output_pub.publish(target_tick)
            
            # 每秒打印一次日志（便于调试，清晰展示各参数状态，与旋转轴日志风格统一）
            rospy.loginfo_throttle(1, 
                f"🔄 摆动轴 | 当前角度:{self.current_swing_deg:.2f}° | "
                f"增量指令:{self.target_delta_deg:.2f}° | "
                f"目标角度:{self.target_reach_deg:.2f}° | "
                f"下发编码:{target_tick}"
            )
            
            self.rate.sleep()

if __name__ == "__main__":
    try:
        node = SwingSimple()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("❌ 摆动轴节点停止")
    except Exception as e:
        # 异常捕获日志，便于排查运行错误（与旋转轴节点规范统一）
        rospy.logerr(f"❌ 摆动轴节点运行异常：{str(e)}")