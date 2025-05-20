#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
from geometry_msgs.msg import Pose
from flask import Flask, request, jsonify

app = Flask(__name__)

# Инициализация MoveIt и ROS без перехвата сигналов Flask
moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('move_to_xyz_rest', anonymous=True, disable_signals=True)

# Настройка группы манипулятора
arm = moveit_commander.MoveGroupCommander("manipulator")
arm.set_planning_time(5.0)
arm.set_num_planning_attempts(3)
arm.set_goal_orientation_tolerance(0.01)
arm.set_max_velocity_scaling_factor(0.5)
arm.set_max_acceleration_scaling_factor(0.5)
arm.set_start_state_to_current_state()

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json(force=True)
    # Проверяем входные параметры
    required = ['x','y','z','qx','qy','qz','qw']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify(success=False, error=f"Missing parameter(s): {', '.join(missing)}"), 400

    # Формируем целевую позу
    target = Pose()
    target.position.x = data['x']
    target.position.y = data['y']
    target.position.z = data['z']
    target.orientation.x = data['qx']
    target.orientation.y = data['qy']
    target.orientation.z = data['qz']
    target.orientation.w = data['qw']

    # Планирование
    arm.set_pose_target(target, end_effector_link="gripper_tip")
    try:
        plan = arm.plan()
    except Exception as e:
        arm.clear_pose_targets()
        return jsonify(success=False, error=f"planning_exception: {str(e)}"), 500

    # Извлекаем траекторию из результата plan()
    traj = plan[1] if isinstance(plan, tuple) else plan
    if not getattr(traj, 'joint_trajectory', None) or not traj.joint_trajectory.points:
        arm.clear_pose_targets()
        return jsonify(success=False, error="planning_failed"), 400

    # Асинхронное исполнение, чтобы сразу вернуть ответ
    try:
        arm.execute(traj, wait=False)
    except Exception as e:
        arm.clear_pose_targets()
        return jsonify(success=False, error=f"execution_exception: {str(e)}"), 500

    # Сбрасываем цели — joint_states будут отдаваться через rosbridge
    arm.clear_pose_targets()
    return jsonify(success=True)

if __name__ == '__main__':
    # Запускаем Flask-сервер на всех интерфейсах, порт 5000
    app.run(host='0.0.0.0', port=5000, threaded=True)
