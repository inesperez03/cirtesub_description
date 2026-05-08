import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


ROBOT_VARIANT_TO_ARMS = {
    "dual_alpha": "dual",
    "single_alpha": "single",
    "auv": "auv",
}


def resolve_arms(arms, robot_variant):
    if arms:
        if arms not in ("dual", "single", "auv"):
            raise RuntimeError(
                "Unsupported arms '{}'. Use 'dual', 'single' or 'auv'.".format(arms)
            )
        return arms

    if robot_variant not in ROBOT_VARIANT_TO_ARMS:
        raise RuntimeError(
            "Unsupported robot_variant '{}'. Use 'dual_alpha', 'single_alpha' or 'auv'.".format(
                robot_variant
            )
        )
    return ROBOT_VARIANT_TO_ARMS[robot_variant]


def launch_setup(context, *args, **kwargs):
    robot_namespace = LaunchConfiguration("robot_namespace").perform(context).strip("/")
    robot_variant = LaunchConfiguration("robot_variant").perform(context)
    arms = resolve_arms(LaunchConfiguration("arms").perform(context), robot_variant)
    environment = LaunchConfiguration("environment").perform(context)

    if arms in ("dual", "single"):
        xacro_name = "cirtesub_dual_alpha.urdf.xacro"
    elif arms == "auv":
        xacro_name = "cirtesub.urdf.xacro"

    if environment not in ("sim", "real"):
        raise RuntimeError(
            f"Unsupported environment '{environment}'. Use 'sim' or 'real'."
        )

    description_pkg = get_package_share_directory("cirtesub_description")
    hardware_pkg = get_package_share_directory("sura_hardware_interface")
    xacro_file = os.path.join(description_pkg, "urdf", xacro_name)
    csv_file = os.path.join(hardware_pkg, "config", "t500_lookup.csv")

    xacro_command = [
        "xacro ",
        xacro_file,
        " robot_namespace:=",
        robot_namespace,
        " environment:=",
        environment,
        " lookup_csv:=",
        csv_file,
        " stonefish_topic:=/",
        robot_namespace,
        "/controller/thruster_setpoints_sim",
    ]

    if arms in ("dual", "single"):
        alpha_use_sim = "true" if environment == "sim" else "false"
        xacro_command.extend(
            [
                " arms:=",
                arms,
                " use_sim:=",
                alpha_use_sim,
                " alpha_use_fake_hardware:=",
                LaunchConfiguration("alpha_use_fake_hardware"),
                " alpha_left_serial_port:=",
                LaunchConfiguration("alpha_left_serial_port"),
                " alpha_right_serial_port:=",
                LaunchConfiguration("alpha_right_serial_port"),
                " alpha_left_state_update_frequency:=",
                LaunchConfiguration("alpha_left_state_update_frequency"),
                " alpha_right_state_update_frequency:=",
                LaunchConfiguration("alpha_right_state_update_frequency"),
                " initial_positions_file:=",
                LaunchConfiguration("initial_positions_file"),
                " alpha_desired_joint_states_topic:=/",
                robot_namespace,
                "/alpha/desired_joint_states",
                " alpha_joint_states_topic:=/",
                robot_namespace,
                "/alpha/joint_states",
            ]
        )

    robot_description = Command(xacro_command)

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            namespace=robot_namespace,
            output="screen",
            parameters=[{"robot_description": robot_description}],
            remappings=[
                ("/robot_description", f"/{robot_namespace}/robot_description"),
                ("/joint_states", f"/{robot_namespace}/joint_states"),
            ],
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("robot_namespace", default_value="sura"),
            DeclareLaunchArgument("robot_variant", default_value="dual_alpha"),
            DeclareLaunchArgument("arms", default_value=""),
            DeclareLaunchArgument("environment", default_value="sim"),
            DeclareLaunchArgument("alpha_use_fake_hardware", default_value="true"),
            DeclareLaunchArgument("alpha_left_serial_port", default_value=""),
            DeclareLaunchArgument("alpha_right_serial_port", default_value=""),
            DeclareLaunchArgument("alpha_left_state_update_frequency", default_value="250"),
            DeclareLaunchArgument("alpha_right_state_update_frequency", default_value="250"),
            DeclareLaunchArgument("initial_positions_file", default_value="initial_positions.yaml"),
            OpaqueFunction(function=launch_setup),
        ]
    )
