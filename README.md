# PRISM — Floor-Plan-Guided Semantic Navigation (ROS 2)

**Plan from floor plan · Refine with SLAM · Identify objects · Move semantically**

A ROS 2 Jazzy + Gazebo Harmonic indoor robot that is being built to navigate a home on its
very first run using only a floor-plan image, while SLAM corrects the map live and an RGB-D
perception layer labels objects for semantic goals ("go to kitchen", "find the chair").

## Status

| Module | Status |
|---|---|
| Differential-drive robot (URDF/xacro) in furnished 2BHK world | ✅ Done |
| Sensor suite: 2D LiDAR, IMU, RGB-D camera, wheel encoders | ✅ Done |
| Depth colorizer node (TURBO colormap, Python/OpenCV) | ✅ Done |
| EKF state estimation (wheel odometry + IMU) | 🔄 In progress |
| SLAM mapping (slam_toolbox) + Nav2 navigation | ⏳ Planned |
| Floor-plan → room/door graph → Nav2 waypoints (C++) | ⏳ Planned |
| YOLOv8 + depth semantic mapping | ⏳ Planned |

## Tech stack
ROS 2 Jazzy · Gazebo Harmonic · ros_gz_bridge · RViz2 · robot_localization · slam_toolbox · Nav2 · OpenCV · Python · C++

## Run it

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/akashakhade/prism-floorplan-nav.git mobile_robot
cd ~/ros2_ws
colcon build --symlink-install --packages-select mobile_robot
source install/setup.bash
ros2 launch mobile_robot launch_sim.launch.py
```

Drive it (new terminal):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=cmd_vel_teleop
```

Teleop publishes to `/cmd_vel_teleop`; the `safety_stop` node filters it with the LiDAR
(slows down near obstacles, stops at 0.35 m) and forwards the safe command to `/cmd_vel`.

## Topics

| Topic | Type | Source |
|---|---|---|
| `/scan` | LaserScan | 360° GPU LiDAR |
| `/imu` | Imu | IMU @ 100 Hz |
| `/camera/image`, `/camera/depth_image`, `/camera/points` | Image / PointCloud2 | RGB-D camera |
| `/camera/depth_colored` | Image | depth_colorizer node |
| `/odom`, `/joint_states` | Odometry / JointState | Diff-drive + encoders |
| `/cmd_vel_teleop` | Twist | Teleop (raw, unfiltered) |
| `/cmd_vel` | Twist | safety_stop (LiDAR-filtered) → Gazebo |

## Author
**Akash Akhade** — B.E. Computer Engineering · [GitHub](https://github.com/akashakhade)