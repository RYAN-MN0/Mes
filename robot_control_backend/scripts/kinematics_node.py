#!/usr/bin/env python3
import rospy
import math
from std_msgs.msg import Header
from robot_control_backend.msg import (
    Kinematics,
    RotationCmd,    # 你给的旋转轴msg
    SwingCmd,       # 你给的摆动轴msg
    TelescopicCmd   # 你给的伸长轴msg
)

class IKCalculationNode:
    def __init__(self):
        rospy.init_node('ik_calculation_node', anonymous=True)
        
        # 订阅坐标指令
        self.coord_sub = rospy.Subscriber(
            '/control/kinematics_cmd',
            Kinematics,
            self.coordinate_callback,
            queue_size=10
        )

        # ==============================
        # ✅ 按你提供的 MSG 格式发布
        # ==============================
        self.rotation_pub = rospy.Publisher(
            '/control/kinematics_rotation_cmd',
            RotationCmd,
            queue_size=10
        )
        self.swing_pub = rospy.Publisher(
            '/control/kinematics_swing_cmd',
            SwingCmd,
            queue_size=10
        )
        self.telescopic_pub = rospy.Publisher(
            '/control/kinematics_telescopic_cmd',
            TelescopicCmd,
            queue_size=10
        )
        
        rospy.loginfo("✅ 逆运动学解算节点已启动！")

    def coordinate_callback(self, msg):
        # 只处理 device_id = 0（坐标指令）
        if msg.device_id != 0:
            rospy.logwarn("⚠️  设备编号无效，不是坐标指令！跳过解算")
            return
        
        if len(msg.position) != 3:
            rospy.logwarn("⚠️  坐标格式错误，需要 [x,y,z]")
            return
        
        x = msg.position[0]
        y = msg.position[1]
        z = msg.position[2]

        try:
            # ----------------------
            # 逆运动学计算
            # ----------------------
            theta1 = math.atan2(y, x)
            theta1_deg = math.degrees(theta1)

            L = math.sqrt(x**2 + y**2 + z**2)

            if L < 1e-6:
                theta2_deg = 0.0
            else:
                sin_theta2 = z / L
                sin_theta2 = max(min(sin_theta2, 1.0), -1.0)
                theta2 = math.asin(sin_theta2)
                theta2_deg = math.degrees(theta2)

            # ----------------------
            # 旋转轴 device_id=33
            # ----------------------
            rot_msg = RotationCmd()
            rot_msg.header = Header()
            rot_msg.header.stamp = rospy.Time.now()
            rot_msg.module_id = 17
            rot_msg.device_id = 33
            rot_msg.position = [theta1_deg]  # float64[] 数组
            self.rotation_pub.publish(rot_msg)

            # ----------------------
            # 摆动轴 device_id=34
            # ----------------------
            swing_msg = SwingCmd()
            swing_msg.header = Header()
            swing_msg.header.stamp = rospy.Time.now()
            swing_msg.module_id = 17
            swing_msg.device_id = 34
            swing_msg.position = [theta2_deg]
            self.swing_pub.publish(swing_msg)

            # ----------------------
            # 伸长轴 device_id=35
            # ----------------------
            tel_msg = TelescopicCmd()
            tel_msg.header = Header()
            tel_msg.header.stamp = rospy.Time.now()
            tel_msg.module_id = 17
            tel_msg.device_id = 35
            tel_msg.position = [L]
            self.telescopic_pub.publish(tel_msg)

            rospy.loginfo(f"✅ 解算完成：旋转={theta1_deg:.2f}° 摆动={theta2_deg:.2f}° 长度={L:.2f}mm")

        except Exception as e:
            rospy.logerr(f"❌ 解算错误：{str(e)}")

if __name__ == '__main__':
    try:
        ik_node = IKCalculationNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass