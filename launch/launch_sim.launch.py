import os
import re

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def get_world_name(sdf_path, fallback='default'):
    """Read <world name="..."> from the .sdf so the bridge topics always match."""
    with open(sdf_path, 'r') as f:
        match = re.search(r'<world\s+name="([^"]+)"', f.read())
    return match.group(1) if match else fallback


def generate_launch_description():

    package_name = 'mobile_robot'
    pkg_share = get_package_share_directory(package_name)

    world_file = os.path.join(pkg_share, 'worlds', 'two_bhk_realistic_world.sdf')
    world_name = get_world_name(world_file)

    rviz_config = os.path.join(pkg_share, 'config', 'view.rviz')
    rviz_args = ['-d', rviz_config] if os.path.exists(rviz_config) else []

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Gazebo Harmonic
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r ' + world_file}.items()
    )

    # Spawn robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'mobile_robot', '-z', '0.15'],
        output='screen'
    )

    # Bridge ( [ = Gazebo->ROS,  ] = ROS->Gazebo )
    # NOTE: Gazebo's odom->base_link TF is NOT bridged; the EKF publishes it.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # time + control
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # odometry + joints (encoders)
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'/world/{world_name}/model/mobile_robot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            # LiDAR
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/scan/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            # IMU
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            # RGB-D camera
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        remappings=[
            (f'/world/{world_name}/model/mobile_robot/joint_state', '/joint_states'),
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # EKF: fuses wheel odometry + IMU, publishes odom -> base_link
    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[
            os.path.join(pkg_share, 'config', 'ekf.yaml'),
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # Colour-mapped depth image
    depth_colorizer = Node(
        package='mobile_robot',
        executable='depth_colorizer',
        parameters=[{
            'use_sim_time': True,
            'min_depth': 0.1,
            'max_depth': 6.0
        }],
        output='screen'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=rviz_args,
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([rsp, gazebo, spawn_robot, bridge, ekf, depth_colorizer, rviz])