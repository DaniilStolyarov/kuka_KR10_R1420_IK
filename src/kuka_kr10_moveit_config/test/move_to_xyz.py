#!/usr/bin/env python

import sys
import rospy
import moveit_commander
import geometry_msgs.msg

if len(sys.argv) != 8:
    print("Usage: move_to_xyz.py x y z qx qy qz qw")
    sys.exit(1)

x = float(sys.argv[1])
y = float(sys.argv[2])
z = float(sys.argv[3])
qx = float(sys.argv[4])
qy = float(sys.argv[5])
qz = float(sys.argv[6])
qw = float(sys.argv[7])

# Инициализация
moveit_commander.roscpp_initialize([])
rospy.init_node('move_to_xyz_node', anonymous=True)

group = moveit_commander.MoveGroupCommander("manipulator")

# Создание цели
pose_target = geometry_msgs.msg.Pose()
pose_target.position.x = x
pose_target.position.y = y
pose_target.position.z = z
pose_target.orientation.x = qx
pose_target.orientation.y = qy
pose_target.orientation.z = qz
pose_target.orientation.w = qw

group.set_pose_target(pose_target)
group.set_goal_orientation_tolerance(0.1)  # Можем чуть ужесточить теперь
group.set_planning_time(5.0)
group.set_num_planning_attempts(10)
plan = group.go(wait=True)

group.stop()
joints = group.get_current_joint_values()
print(joints)
group.clear_pose_targets()

moveit_commander.roscpp_shutdown()
