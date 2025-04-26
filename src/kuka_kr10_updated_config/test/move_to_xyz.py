#!/usr/bin/env python3

import sys
import rospy
import moveit_commander
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState

def main():
    if len(sys.argv) != 8:
        print("Usage: move_to_xyz.py x y z qx qy qz qw")
        sys.exit(1)
    x, y, z, qx, qy, qz, qw = map(float, sys.argv[1:])

    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_to_xyz_node', anonymous=True)

    arm = moveit_commander.MoveGroupCommander("manipulator")
    arm.set_planning_time(5.0)
    arm.set_num_planning_attempts(3)
    arm.set_goal_orientation_tolerance(0.01)
    arm.set_max_velocity_scaling_factor(0.5)
    arm.set_max_acceleration_scaling_factor(0.5)
    arm.set_start_state_to_current_state()

    # цель по позе
    target = Pose()
    target.position.x = x
    target.position.y = y
    target.position.z = z
    target.orientation.x = qx
    target.orientation.y = qy
    target.orientation.z = qz
    target.orientation.w = qw
    arm.set_pose_target(target, end_effector_link="gripper_tip")

    # план + исполнение
    plan_result = arm.plan()
    # выдираем RobotTrajectory
    traj = plan_result[1] if isinstance(plan_result, tuple) else plan_result
    if not traj.joint_trajectory.points:
        rospy.logerr("❌ Планирование не удалось")
        return

    arm.execute(traj, wait=True)
        # после arm.execute(...)
    arm.stop()
    arm.clear_pose_targets()
    rospy.sleep(0.1)

    # читаем реальные joint_states прямо из fake_controller_joint_states
    try:
        js = rospy.wait_for_message(
            '/move_group/fake_controller_joint_states',
            JointState,
            timeout=2.0)
        print("→ fake_controller_joint_states:", js.position)
    except rospy.ROSException:
        rospy.logerr("Не дождались /move_group/fake_controller_joint_states")


    moveit_commander.roscpp_shutdown()

if __name__ == "__main__":
    main()
