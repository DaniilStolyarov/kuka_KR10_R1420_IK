#!/usr/bin/env python3
import sys
import rospy
import moveit_commander
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState
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
    for k in ('x','y','z','qx','qy','qz','qw'):
        if k not in data:
            return jsonify(success=False, error=f"Missing parameter: {k}"), 400

    # Формируем Pose
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
    plan = arm.plan()
    traj = plan[1] if isinstance(plan, tuple) else plan
    if not traj.joint_trajectory.points:
        return jsonify(success=False, error="planning_failed"), 400

    # Исполнение
    arm.execute(traj, wait=True)
    arm.stop()
    arm.clear_pose_targets()
    rospy.sleep(0.1)

    # Читаем фактические joint_states
    try:
        js = rospy.wait_for_message(
            '/move_group/fake_controller_joint_states',
            JointState,
            timeout=2.0
        )
    except rospy.ROSException:
        return jsonify(success=False, error="no_joint_states_received"), 500

    # Возвращаем JSON с 6 позициями суставов
    return jsonify(
        success=True,
        joint_state={
            'name': js.name,
            'position': js.position
        }
    )

if __name__ == '__main__':
    # Запускаем Flask-сервер на всех интерфейсах, порт 5000
    app.run(host='0.0.0.0', port=5000, threaded=True)
