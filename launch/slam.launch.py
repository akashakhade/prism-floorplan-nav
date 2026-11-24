import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    """Start slam_toolbox (online async mapping) with PRISM's parameters."""
    pkg_share = get_package_share_directory('mobile_robot')
    slam_params = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')

    # Use slam_toolbox's own launch file: it also configures + activates the
    # lifecycle node (Jazzy), so the map starts publishing automatically.
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'),
                         'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_params,
        }.items()
    )

    return LaunchDescription([slam])
