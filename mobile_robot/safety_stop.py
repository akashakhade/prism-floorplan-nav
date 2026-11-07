import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class SafetyStop(Node):
    """Filters velocity commands using LiDAR: slows/stops before obstacles."""

    def __init__(self):
        super().__init__('safety_stop')

        self.declare_parameter('input_topic', '/cmd_vel_teleop')
        self.declare_parameter('output_topic', '/cmd_vel')
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('front_stop_distance', 0.35)   # m from LiDAR
        self.declare_parameter('front_slow_distance', 0.70)   # m from LiDAR
        self.declare_parameter('rear_stop_distance', 0.30)    # m from LiDAR
        self.declare_parameter('sector_deg', 35.0)            # +/- cone width
        self.declare_parameter('rate', 20.0)                  # Hz
        self.declare_parameter('cmd_timeout', 0.5)            # s without cmd -> stop
        self.declare_parameter('scan_timeout', 0.5)           # s without scan -> stop

        gp = self.get_parameter
        self.front_stop = float(gp('front_stop_distance').value)
        self.front_slow = float(gp('front_slow_distance').value)
        self.rear_stop = float(gp('rear_stop_distance').value)
        self.half_sector = math.radians(float(gp('sector_deg').value))
        self.cmd_timeout = float(gp('cmd_timeout').value)
        self.scan_timeout = float(gp('scan_timeout').value)

        self.cmd = Twist()
        self.front_min = math.inf
        self.rear_min = math.inf
        self.last_cmd_time = None    # time of the last velocity command
        self.last_scan_time = None   # time of the last LiDAR scan

        self.create_subscription(
            LaserScan, gp('scan_topic').value, self.scan_cb, qos_profile_sensor_data)
        self.create_subscription(
            Twist, gp('input_topic').value, self.cmd_cb, 10)
        self.pub = self.create_publisher(Twist, gp('output_topic').value, 10)
        self.create_timer(1.0 / float(gp('rate').value), self.timer_cb)

        self.get_logger().info(
            f'Safety stop active: front stop {self.front_stop} m, '
            f'slow {self.front_slow} m, rear stop {self.rear_stop} m'
        )

    def scan_cb(self, msg):
        front, rear = math.inf, math.inf
        for i, r in enumerate(msg.ranges):
            if not math.isfinite(r) or r < msg.range_min or r > msg.range_max:
                continue
            a = msg.angle_min + i * msg.angle_increment
            a = math.atan2(math.sin(a), math.cos(a))   # wrap to [-pi, pi]
            if abs(a) <= self.half_sector:
                front = min(front, r)
            elif abs(a) >= math.pi - self.half_sector:
                rear = min(rear, r)
        self.front_min, self.rear_min = front, rear
        self.last_scan_time = self.get_clock().now()

    def cmd_cb(self, msg):
        self.cmd = msg
        self.last_cmd_time = self.get_clock().now()

    def age(self, stamp):
        """Seconds since stamp (infinite if never received)."""
        if stamp is None:
            return math.inf
        return (self.get_clock().now() - stamp).nanoseconds * 1e-9

    def timer_cb(self):
        out = Twist()

        # Fail safe 1: teleop stopped sending -> full stop (linear AND angular)
        if self.age(self.last_cmd_time) > self.cmd_timeout:
            self.pub.publish(out)
            return

        out.angular.z = self.cmd.angular.z     # turning in place is always allowed
        v = self.cmd.linear.x

        # Fail safe 2: no fresh LiDAR -> no forward/backward motion
        if self.age(self.last_scan_time) > self.scan_timeout:
            if v != 0.0:
                self.get_logger().warn(
                    'No recent LiDAR scan - blocking linear motion',
                    throttle_duration_sec=2.0)
            v = 0.0
        elif v > 0.0:
            if self.front_min <= self.front_stop:
                v = 0.0
                self.get_logger().warn(
                    f'Obstacle ahead at {self.front_min:.2f} m - stopping',
                    throttle_duration_sec=2.0)
            elif self.front_min < self.front_slow:
                scale = (self.front_min - self.front_stop) / (self.front_slow - self.front_stop)
                v *= scale
        elif v < 0.0:
            if self.rear_min <= self.rear_stop:
                v = 0.0
                self.get_logger().warn(
                    f'Obstacle behind at {self.rear_min:.2f} m - stopping',
                    throttle_duration_sec=2.0)

        out.linear.x = v
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = SafetyStop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()