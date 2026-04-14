#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
import rospy
import threading
from robot_control_backend.msg import RotationCmd, SwingCmd, TelescopicCmd
from robot_control_backend.msg import Feedback,Kinematics

# ======================= 全局变量 =======================
connected_clients = set()
loop = None  # 全局事件循环（用于桥接ROS和asyncio）
lock = threading.Lock()  # 线程锁，保护全局变量（客户端列表）

# ROS发布者（全局初始化，严格对应要求的4个发布话题）
kinematics_pose_pub = None       # /control/kinematics_pose（目标坐标指令）
adjust_rot_pub = None           # /control/adjust_rotation_cmd（旋转轴微调）
adjust_swing_pub = None         # /control/adjust_swing_cmd（摆动轴微调）
adjust_telescopic_pub = None    # /control/adjust_telescopic_cmd（伸长轴微调）


# ======================= ROS 回调（接收下位机反馈，转发给Java+拆分反馈话题）=======================
def ros_feedback_callback(msg):
    """订阅各反馈话题，解析反馈数据（区分旋转/摆动/伸缩轴与压力传感器格式），转发给Java前端，并拆分发布各轴反馈话题"""
    global loop, telescope_feedback_pub

    # 区分反馈类型，按对应格式解析数据（旋转轴、摆动轴、伸缩轴共用一种格式，压力传感器单独格式）
    if msg.device_id in [33, 34, 35]:
        # 旋转轴（33）、摆动轴（34）、伸缩轴（35）数据格式
        feedback_data = {
            "time_id": rospy.get_time(),  # 用时间戳作为消息id，避免重复
            "header": {
                "stamp": {
                    "secs": msg.header.stamp.secs,
                    "nsecs": msg.header.stamp.nsecs
                },
                "frame_id": msg.header.frame_id
            },
            "module_id": msg.module_id,
            "device_id": msg.device_id,
            "position": msg.position,  # float64[] 类型，旋转/摆动轴为角度（度），伸缩轴为长度，符合格式要求
            "data_type": "axis_encoder"  # 标注为轴类编码器数据
        }
    elif msg.device_id == 49:
        # 压力传感器数据格式（单独解析，含id自增字段）
        feedback_data = {
            "time_id": rospy.get_time(),  # 用时间戳辅助去重，结合msg.id确保不重复
            "header": {
                "stamp": {
                    "secs": msg.header.stamp.secs,
                    "nsecs": msg.header.stamp.nsecs
                },
                "frame_id": msg.header.frame_id
            },
            "id": msg.id ,
            "module_id": msg.module_id,  
            "device_id": msg.device_id,
            "position": msg.position,  # int32[] 类型，压力数据（单位：N），符合格式要求
            "data_type": "pressure_sensor"  # 标注为压力传感器数据
        }
    else:
        # 未知反馈部件，按通用格式解析
        feedback_data = {
            "time_id": rospy.get_time(),
            "header": {
                "stamp": {
                    "secs": msg.header.stamp.secs,
                    "nsecs": msg.header.stamp.nsecs
                },
                "frame_id": msg.header.frame_id
            },
            "module_id": msg.module_id,
            "device_id": msg.device_id,
            "position": msg.position,
            "data_type": "unknown"
        }

    # 标注反馈类型，便于前端解析（与数据格式对应）
    if msg.device_id == 33:
        feedback_data["feedback_type"] = "旋转轴编码器"
    elif msg.device_id == 34:
        feedback_data["feedback_type"] = "摆动轴编码器"
    elif msg.device_id == 35:
        feedback_data["feedback_type"] = "伸长轴编码器"
        # 新增：发布伸缩轴反馈话题 /hardware/telescope_feedback（数据格式匹配伸缩轴要求）
        if telescope_feedback_pub:
            telescope_feedback_pub.publish(msg)
    elif msg.device_id == 49:
        feedback_data["feedback_type"] = "压力传感器"
    else:
        feedback_data["feedback_type"] = "未知反馈部件"

    # 转换为JSON格式，确保数据类型正确（float64[]/int32[] 转列表，适配前端解析）
    json_feedback = json.dumps(feedback_data)

    # 线程安全，将反馈数据发送给所有Java客户端
    if loop and not loop.is_closed():
        loop.call_soon_threadsafe(
            asyncio.create_task,
            send_to_all_clients(json_feedback)
        )

# ======================= 异步发送消息（仅在asyncio循环中运行）=======================
async def send_to_all_clients(json_data):
    # 复制客户端列表，避免迭代时被修改（加锁保护）
    with lock:
        clients_to_send = list(connected_clients)  # 用list()安全复制set

    # 遍历所有连接的Java客户端，发送数据
    for websocket in clients_to_send:
        try:
            await websocket.send(json_data)
        except Exception as e:
            rospy.logerr(f"❌ 反馈数据发送失败: {str(e)}")
            # 发送失败，移除异常客户端并关闭连接
            with lock:
                if websocket in connected_clients:
                    connected_clients.remove(websocket)
            try:
                await websocket.close()
            except Exception:
                pass

# ======================= WebSocket 处理（接收Java指令，解析并发布ROS话题）=======================
async def handle_java(websocket):
    rospy.loginfo("✅ Java 客户端已连接")
    # 新客户端加入（加锁保护）
    with lock:
        connected_clients.add(websocket)
    
    try:
        async for msg in websocket:
            rospy.loginfo(f"📥 接收Java指令: {msg}")
            # 解析Java发送的JSON指令
            try:
                cmd_data = json.loads(msg)
                device_id = cmd_data.get("device_id")
                position = cmd_data.get("position")
                module_id = cmd_data.get("module_id")  
                
                if device_id == 0:
                    # 发布目标坐标指令到 /control/kinematics_pose（对应要求0）
                    kinematics_cmd = Kinematics()
                    kinematics_cmd.header = rospy.Header()
                    kinematics_cmd.module_id = module_id 
                    kinematics_cmd.device_id = 0
                    kinematics_cmd.position = position
                    kinematics_pose_pub.publish(kinematics_cmd)
                    rospy.loginfo(f"📤 发布目标坐标指令（device id=0），坐标值：{position}，话题：/control/kinematics_pose")

                elif device_id == 33:
                    # 旋转轴微调指令（对应要求2）
                    rot_cmd = RotationCmd()
                    rot_cmd.header = rospy.Header()
                    rot_cmd.module_id = module_id  # 模块编号，默认X1Y1
                    rot_cmd.device_id = 33
                    rot_cmd.position = position  # 角度（度），float64[] 类型
                    adjust_rot_pub.publish(rot_cmd)
                    rospy.loginfo(f"📤 发布旋转轴微调指令（device id=33），角度值：{position}，话题：/control/adjust_rotation_cmd")

                elif device_id == 34:
                    # 摆动轴微调指令（对应要求3）
                    swing_cmd = SwingCmd()
                    swing_cmd.header = rospy.Header()
                    swing_cmd.module_id = module_id  # 模块编号，默认X1Y1
                    swing_cmd.device_id = 34
                    swing_cmd.position = position  # 角度（度），float64[] 类型
                    adjust_swing_pub.publish(swing_cmd)
                    rospy.loginfo(f"📤 发布摆动轴微调指令（device id=34），角度值：{position}，话题：/control/adjust_swing_cmd")

                elif device_id == 35:
                    # 伸长轴微调指令（对应要求4）
                    telescopic_cmd = TelescopicCmd()
                    telescopic_cmd.header = rospy.Header()
                    telescopic_cmd.module_id = module_id  # 模块编号，默认X1Y1
                    telescopic_cmd.device_id = 35
                    telescopic_cmd.position = position 
                    adjust_telescopic_pub.publish(telescopic_cmd)
                    rospy.loginfo(f"📤 发布伸长轴微调指令（device id=35），长度值：{position}，话题：/control/adjust_telescopic_cmd")

                else:
                    rospy.logwarn(f"⚠️  无效的device id：{device_id}（仅支持0/32/33/34）")

            except json.JSONDecodeError:
                rospy.logerr("❌ Java指令解析失败：不是合法的JSON格式")
            except Exception as e:
                rospy.logerr(f"❌ 指令处理异常：{str(e)}")
    
    finally:
        # 移除客户端，确保线程安全
        with lock:
            if websocket in connected_clients:
                connected_clients.remove(websocket)
        rospy.loginfo("❌ Java 客户端已断开")

# ======================= ROS 自旋线程（解决asyncio与ROS线程冲突）=======================
def ros_spin_thread():
    """独立线程运行ROS自旋，保证回调正常触发"""
    rospy.spin()

# ======================= 主函数（初始化ROS和WebSocket，完善话题订阅/发布）=======================
async def main():
    global loop, kinematics_pose_pub, adjust_rot_pub, adjust_swing_pub, adjust_telescopic_pub, telescope_feedback_pub
    loop = asyncio.get_running_loop()

    # 1. 初始化ROS节点
    rospy.init_node("web_data_node", anonymous=True)
    rospy.loginfo("🚀 web_data_node 节点初始化完成")

    # 2. 初始化ROS发布者（严格对应要求的4个发布话题）
    kinematics_pose_pub = rospy.Publisher("/control/kinematics_pose", Kinematics, queue_size=10)  # 目标坐标指令
    adjust_rot_pub = rospy.Publisher("/control/adjust_rotation_cmd", RotationCmd, queue_size=10)  # 旋转轴微调
    adjust_swing_pub = rospy.Publisher("/control/adjust_swing_cmd", SwingCmd, queue_size=10)      # 摆动轴微调
    adjust_telescopic_pub = rospy.Publisher("/control/adjust_telescopic_cmd", TelescopicCmd, queue_size=10)  # 伸长轴微调

    # 3. 订阅下位机反馈话题（严格对应要求的4个订阅话题，反馈节点发布的数据格式已适配）
    # 订阅旋转轴反馈：/hardware/rotation_feedback（旋转轴格式，float64[] position，角度单位）
    rospy.Subscriber("/hardware/rotation_feedback", Feedback, ros_feedback_callback)
    # 订阅摆动轴反馈：/hardware/swing_feedback（摆动轴格式，float64[] position，角度单位）
    rospy.Subscriber("/hardware/swing_feedback", Feedback, ros_feedback_callback)
    # 订阅伸缩轴反馈：/hardware/telescope_feedback（伸缩轴格式，float64[] position，长度单位）
    rospy.Subscriber("/hardware/telescope_feedback", Feedback, ros_feedback_callback)
    # 订阅压力传感器反馈：/hardware/sensor_feedback（压力传感器格式，int32[] position，单位N，含id自增）
    rospy.Subscriber("/hardware/sensor_feedback", Feedback, ros_feedback_callback)
    rospy.loginfo("✅ 已完成所有反馈话题订阅：rotation_feedback、swing_feedback、telescope_feedback、sensor_feedback")

    # 4. 启动独立ROS自旋线程（解决asyncio与ROS冲突）
    spin_thread = threading.Thread(target=ros_spin_thread, daemon=True)
    spin_thread.start()
    rospy.loginfo("✅ ROS自旋线程启动成功")

    # 5. 启动WebSocket服务器
    websocket_server = await websockets.serve(handle_java, "0.0.0.0",8760)
    rospy.loginfo("🚀 WebSocket服务器启动成功 ws://0.0.0.0:8760")

    # 保持运行
    await websocket_server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except rospy.ROSInterruptException:
        rospy.loginfo("📤 web_data_node 节点正常停止")
    except Exception as e:
        rospy.logerr(f"❌ web_data_node 运行异常：{str(e)}")
    finally:
        # 确保ROS节点正常关闭
        if not rospy.is_shutdown():
            rospy.signal_shutdown("程序退出")