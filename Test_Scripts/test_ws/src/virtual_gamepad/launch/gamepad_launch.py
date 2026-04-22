from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare("virtual_gamepad").find("virtual_gamepad")

    return LaunchDescription([
         
        Node(
            package="virtual_gamepad",
            executable="virtual_gamepad_node",
            name="virtual_gamepad_node",
            output="screen",
            parameters=[{
            }],
        ),
    ])