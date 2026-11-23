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
| EKF state estimation (wheel odometry + IMU yaw rate) | ✅ Done |
| LiDAR safety stop with dead-man timeout | ✅ Done |
| SLAM mapping (slam_toolbox) | 🔄 Next |
| Nav2 navigation | ⏳ Planned |
| Floor-plan → room/door graph → Nav2 waypoints (C++) | ⏳ Planned |
| YOLOv8 + depth semantic mapping | ⏳ Planned |

## Tech stack
ROS 2 Jazzy · Gazebo Harmonic · ros_gz_bridge · RViz2 · robot_localization · slam_toolbox · Nav2 · OpenCV · Python · C++

## Install

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/akashakhade/prism-floorplan-nav.git mobile_robot
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-select mobile_robot
source install/setup.bash
```

## Run it

```bash
ros2 launch mobile_robot launch_sim.launch.py
```

Drive it (new terminal) — **hold** the key to keep moving:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=cmd_vel_teleop
```

## Safety stop

Teleop publishes to `/cmd_vel_teleop`; the `safety_stop` node filters it and forwards the safe
command to `/cmd_vel`:

- slows down when an obstacle is within 0.70 m and stops at 0.35 m (front), 0.30 m (rear)
- **dead-man switch:** no command for 1 s → full stop (so a crashed teleop/Nav2 cannot run away)
- no LiDAR scan for 0.5 s → forward/backward motion blocked
- invalid parameters are rejected at startup

## Topics

| Topic | Type | Source |
|---|---|---|
| `/scan` | LaserScan | 360° GPU LiDAR @ 10 Hz |
| `/imu` | Imu | IMU @ 50 Hz |
| `/camera/image`, `/camera/depth_image`, `/camera/points` | Image / PointCloud2 | RGB-D camera 320×240 @ 10 Hz |
| `/camera/depth_colored` | Image | depth_colorizer node |
| `/odom`, `/joint_states` | Odometry / JointState | Diff-drive + encoders |
| `/odometry/filtered` + TF `odom → base_link` | Odometry / TF | EKF (robot_localization) |
| `/cmd_vel_teleop` | Twist | Teleop (raw, unfiltered) |
| `/cmd_vel` | Twist | safety_stop (LiDAR-filtered) → Gazebo |

## Tests

```bash
colcon test --packages-select mobile_robot && colcon test-result --verbose
```

## Troubleshooting

- **Simulation slow / robot jerky:** a previous Gazebo server may still be running in the
  background. After stopping the launch, run `pkill -f "gz sim"`.
- **Build error after deleting a file** (`can't copy ... doesn't exist`):
  `rm -rf build/mobile_robot install/mobile_robot` and build again.
- **`Package 'mobile_robot' not found`:** run `source ~/ros2_ws/install/setup.bash` in that terminal.

## Author
**Akash Akhade** — B.E. Computer Engineering · [GitHub](https://github.com/akashakhade)
