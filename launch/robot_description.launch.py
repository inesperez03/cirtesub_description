import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    robot_namespace = LaunchConfiguration("robot_namespace").perform(context).strip("/")
    robot_description_package = LaunchConfiguration("robot_description_package").perform(context)
    xacro_file = LaunchConfiguration("xacro_file").perform(context)
    xacro_arguments = LaunchConfiguration("xacro_arguments").perform(context)

    if not os.path.isabs(xacro_file):
        xacro_file = os.path.join(get_package_share_directory(robot_description_package), xacro_file)

    xacro_command = ["xacro ", xacro_file, " ", xacro_arguments]

    robot_description = Command(xacro_command)

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": robot_description,
                }
            ],
            remappings=[
                ("/robot_description", f"/{robot_namespace}/robot_description"),
                ("/joint_states", f"/{robot_namespace}/alpha/joint_states"),
            ],
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_namespace", default_value=""),
            DeclareLaunchArgument("robot_description_package", default_value="bluerov_description"),
            DeclareLaunchArgument("xacro_file"),
            DeclareLaunchArgument("xacro_arguments", default_value=""),
            OpaqueFunction(function=launch_setup),
        ]
    )