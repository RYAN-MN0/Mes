#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Header
from robot_control_backend.msg import RotationCmd, Feedback, IntCmd

## -------旋转轴功能节点-------------
class RotationSimple:
    def __init__(self):
        rospy.init_node("rotation_simple_node")
        rospy.loginfo("✅ 旋转轴节点启动")

        # 编码器换算系数（仅用于度转编码发给下位机）
        self.DEGREE_PER_TICK = 0.01248  # 1编码 = 0.01248°

        # 核心变量
        self.target_delta_deg = 0.0     # 指令给的：增量角度（度）
        self.current_angle_deg = 0.0    # 硬件反馈：当前实际角度（度，已由反馈节点转换）
        self.target_reach_deg = 0.0     # 最终要到达的角度 = 当前 + 增量

        # 订阅双指令话题
        rospy.Subscriber("/control/adjust_rotation_cmd", RotationCmd, self.cmd_callback)
        rospy.Subscriber("/control/kinematics_rotation_cmd", RotationCmd, self.cmd_callback)

        # 订阅统一硬件反馈
        rospy.Subscriber("/hardware/rotation_feedback", Feedback, self.feedback_callback)
        
        # 发布输出：发给下位机的IntCmd类型消息（修正发布类型）
        self.output_pub = rospy.Publisher("/hardware/rotation_output", IntCmd, queue_size=10)

        # 控制频率（正确初始化位置）
        self.rate = rospy.Rate(20)  # 20Hz控制频率

    def cmd_callback(self, msg):
        """接收度为单位的增量指令，兼容双话题指令"""
        # 从position数组提取第一个元素作为有效增量角度
        self.target_delta_deg = msg.position[0]
        # 收到指令后立即更新目标角度
        self.target_reach_deg = self.current_angle_deg + self.target_delta_deg
        
        # 区分指令来源（便于调试）
        cmd_topic = msg._connection_header.get('topic', '未知话题')
        if cmd_topic == "/control/adjust_rotation_cmd":
            rospy.loginfo(f"📥 收到旋转轴微调指令：+{self.target_delta_deg:.4f}°")
        elif cmd_topic == "/control/kinematics_rotation_cmd":
            rospy.loginfo(f"📥 收到旋转轴运动学计算指令：+{self.target_delta_deg:.4f}°")

    def feedback_callback(self, msg):
        """从统一反馈中提取旋转轴角度"""
        if msg.device_id == 33:
            # 提取角度值
            self.current_angle_deg = msg.position[0]
            # 反馈更新后重新计算目标角度
            self.target_reach_deg = self.current_angle_deg + self.target_delta_deg
            rospy.logdebug(f"📩 收到旋转轴反馈：当前角度{self.current_angle_deg:.2f}°")

    def run(self):
        """核心运行循环"""
        while not rospy.is_shutdown():
            # 角度转编码（四舍五入为整数）
            target_tick = int(round(self.target_reach_deg / self.DEGREE_PER_TICK))

            # 封装IntCmd消息（修正消息类型，匹配发布者声明）
            int_cmd_msg = IntCmd()
            int_cmd_msg.header = Header()
            int_cmd_msg.header.stamp = rospy.Time.now()  # 时间戳
            int_cmd_msg.module_id = 17                   # 模块ID
            int_cmd_msg.device_id = 33                   # 设备ID
            int_cmd_msg.position = [target_tick ]          # 编码值

            # 发布消息给下位机
            self.output_pub.publish(int_cmd_msg)

            # 每秒打印一次日志（便于调试）
            rospy.loginfo_throttle(1, 
                f"🔄 旋转轴 | 当前角度:{self.current_angle_deg:.2f}° | "
                f"增量指令:{self.target_delta_deg:.2f}° | "
                f"目标角度:{self.target_reach_deg:.2f}° | "
                f"下发编码:{target_tick}"
            )
            # 额外打印发布的完整消息（可选，便于调试）
            rospy.logdebug(f"📤 发布IntCmd：module={int_cmd_msg.module_id}, device_id={int_cmd_msg.device_id}, position={int_cmd_msg.position}")

            self.rate.sleep()

if __name__ == "__main__":
    try:
        node = RotationSimple()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("❌ 旋转轴节点停止")
    except Exception as e:
        rospy.logerr(f"❌ 旋转轴节点运行异常：{str(e)}")