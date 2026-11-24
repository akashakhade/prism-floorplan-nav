import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Start Nav2 (map server + AMCL + planner/controller) on a saved map."""
    pkg_share = get_package_share_directory('mobile_robot')
    nav2_bringup = get_package_share_directory('nav2_bringup')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_share, 'maps', 'two_bhk.yaml'),
        description='Full path to the map yaml file')
    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
        description='Full path to the Nav2 parameters file')

    # Command chain: controller -> velocity_smoother -> collision_monitor
    #   -> /cmd_vel_teleop -> safety_stop -> /cmd_vel -> Gazebo
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'true',
            'autostart': 'true',
        }.items()
    )

    return LaunchDescription([map_arg, params_arg, nav2])
