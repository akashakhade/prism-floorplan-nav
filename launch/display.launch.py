import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'mobile_robot'
    pkg_share = get_package_share_directory(package_name)

    rviz_config = os.path.join(pkg_share, 'config', 'view.rviz')
    rviz_args = ['-d', rviz_config] if os.path.exists(rviz_config) else []

    # Robot State Publisher (wall clock, no Gazebo)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    # Sliders to move the wheel joints
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=rviz_args,
        output='screen'
    )

    return LaunchDescription([rsp, joint_state_publisher_gui, rviz])