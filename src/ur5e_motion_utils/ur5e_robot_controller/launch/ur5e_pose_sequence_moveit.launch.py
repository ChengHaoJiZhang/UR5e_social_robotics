from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    sequence_path = PathJoinSubstitution([
        FindPackageShare('social_robot_behaviors'), 'motions',
        LaunchConfiguration('sequence_file'),
    ])
    return LaunchDescription([
        DeclareLaunchArgument('sequence_file', default_value='handshake.yaml'),
        DeclareLaunchArgument('execute', default_value='false'),
        Node(
            package='ur5e_robot_controller',
            executable='ur5e_pose_sequence_moveit_exe',
            output='screen',
            parameters=[{'sequence_file': sequence_path,
                         'execute': ParameterValue(LaunchConfiguration('execute'), value_type=bool)}],
        ),
    ])
