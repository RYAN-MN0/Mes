#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32  # 下位机收整数，无需额外保留Float32
from robot_control_backend.msg import TelescopeCmd, Feedback  # 导入统一反馈msg

# -------------------伸缩轴功能节点------------------
class TelescopeSimple:
    def __init__(self):
        rospy.init_node("telescope_simple_node")
        rospy.loginfo("✅ 舵机伸缩杆节点启动 —— 螺旋传动模型已加载，适配双指令+统一反馈")

        # 1. 电机参数（保留你提供的原始参数，不修改）
        self.DEGREE_PER_TICK = 0.01248  # 1编码对应度数 0.01248°
        
        # 2. 机械参数（保留你提供的原始参数，不修改）
        self.MM_PER_REV = 0.7           # 电机转一圈(360度)，伸缩杆前进0.7mm
        # 3. 计算复合系数 (1mm 对应多少编码)（保留原始公式，确保单位转换正确）
        self.TICK_PER_MM = (360.0 / self.MM_PER_REV) / self.DEGREE_PER_TICK
        
        rospy.loginfo(f"✅ 参数初始化完成：1mm ≈ {self.TICK_PER_MM:.2f} 编码")

        # 核心变量（与旋转轴、摆动轴节点规范统一，适配增量指令逻辑）
        self.target_delta_mm = 0.0      # 指令给的：增量长度（单位：毫米）
        self.current_length_mm = 0.0    # 当前长度（单位：毫米，已由反馈节点完成编码→mm转换）
        self.target_reach_mm = 0.0      # 最终要到达的长度 = 当前长度 + 增量长度

        # 订阅双指令话题（按其他轴规范，适配微调+运动学计算指令）
        # 1. 前端下发的伸缩轴微调指令
        rospy.Subscriber("/control/adjust_telescopic_cmd", TelescopeCmd, self.cmd_callback)
        # 2. 运动计算节点发布的伸缩轴运动命令
        rospy.Subscriber("/control/kinematics_telescopic_cmd", TelescopeCmd, self.cmd_callback)
        
        # 订阅统一硬件反馈：从/hardware/telescope_feedback提取伸缩轴数据（device_id=43，对应Feedback.msg定义）
        rospy.Subscriber("/hardware/telescope_feedback", Feedback, self.feedback_callback)

        # 发布：发给下位机的控制量（编码值，整数，Int32类型，符合要求）
        self.output_pub = rospy.Publisher("/hardware/telescope_output", Int32, queue_size=10)

        self.rate = rospy.Rate(20)  # 20Hz控制频率，与其他轴节点保持一致

    # 收到指令 → 更新目标增量长度（适配TelescopicCmd.msg格式）
    def cmd_callback(self, msg):
        """接收mm为单位的增量指令（适配TelescopicCmd.msg float64[]格式），兼容双话题指令"""
        # 从TelescopicCmd的position数组提取第一个元素作为有效增量长度（贴合你提供的msg.position=[10.0]格式）
        self.target_delta_mm = msg.position[0]
        # 区分指令来源（便于调试，与其他轴节点日志风格统一）
        cmd_topic = msg._connection_header.get('topic', '未知话题')
        if cmd_topic == "/control/adjust_telescopic_cmd":
            rospy.loginfo(f"📥 收到伸缩轴微调指令：+{self.target_delta_mm:.4f}mm")
        elif cmd_topic == "/control/kinematics_telescopic_cmd":
            rospy.loginfo(f"📥 收到伸缩轴运动学计算指令：+{self.target_delta_mm:.4f}mm")

    # 收到统一反馈 → 更新当前长度（无需自行转换，反馈节点已完成编码→mm）
    def feedback_callback(self, msg):
        """从统一反馈中提取伸缩轴长度（device_id=35，已由反馈节点完成编码→mm转换）"""
        # 只处理伸缩轴的反馈数据（严格匹配Feedback.msg的device_id定义：35=伸长轴编码器）
        if msg.device_id == 35:
            # 提取长度值（position数组第一个元素，单位：mm，适配Feedback.msg float64[]格式）
            self.current_length_mm = msg.position[0]
            # 计算最终目标长度（当前长度 + 指令增量长度）
            self.target_reach_mm = self.current_length_mm + self.target_delta_mm
            # 调试日志：确认反馈数据正常接收（终端调试模式可查看）
            rospy.logdebug(f"📩 收到伸缩轴反馈：当前长度{self.current_length_mm:.2f}mm")

    # 主循环：mm→编码转换，下发下位机
    def run(self):
        while not rospy.is_shutdown():
            # --- 核心逻辑：mm -> 编码（保留你提供的原始转换逻辑，适配下位机整数需求）---
            # 1. 计算原始浮点编码
            raw_tick = self.target_reach_mm * self.TICK_PER_MM
            # 2. 四舍五入取整（下位机只认整数，必须转换）
            target_tick = int(round(raw_tick))
            # 3. 发布给下位机（Int32类型，符合要求）
            self.output_pub.publish(target_tick)
            
            # 日志（与其他轴节点风格统一，清晰展示各参数状态，每秒打印一次）
            rospy.loginfo_throttle(1, 
                f"🔄 伸缩轴 | 当前长度:{self.current_length_mm:.2f}mm | "
                f"增量指令:{self.target_delta_mm:.2f}mm | "
                f"目标长度:{self.target_reach_mm:.2f}mm | "
                f"下发编码:{target_tick}"
            )
            
            self.rate.sleep()

if __name__ == "__main__":
    try:
        node = TelescopeSimple()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("❌ 伸缩杆节点关闭")
    except Exception as e:
        # 异常捕获日志，便于排查运行错误（与旋转轴、摆动轴节点规范统一）
        rospy.logerr(f"❌ 伸缩杆节点运行异常：{str(e)}")