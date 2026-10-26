import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class DepthColorizer(Node):
    """Converts a 32FC1 depth image into a colour-mapped image (near = red, far = blue)."""

    def __init__(self):
        super().__init__('depth_colorizer')

        self.declare_parameter('input_topic', '/camera/depth_image')
        self.declare_parameter('output_topic', '/camera/depth_colored')
        self.declare_parameter('min_depth', 0.1)   # metres
        self.declare_parameter('max_depth', 6.0)   # metres

        self.min_depth = float(self.get_parameter('min_depth').value)
        self.max_depth = float(self.get_parameter('max_depth').value)
        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, input_topic, self.callback, 10)
        self.pub = self.create_publisher(Image, output_topic, 10)

        self.get_logger().info(
            f'Colourising {input_topic} -> {output_topic} '
            f'({self.min_depth}-{self.max_depth} m)'
        )

    def callback(self, msg):
        depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        depth = np.asarray(depth, dtype=np.float32)

        # inf / nan / zero = no valid reading
        invalid = ~np.isfinite(depth) | (depth <= 0.0)

        clipped = np.clip(depth, self.min_depth, self.max_depth)
        norm = (clipped - self.min_depth) / (self.max_depth - self.min_depth)

        # invert so near = red, far = blue
        scaled = ((1.0 - norm) * 255.0).astype(np.uint8)
        colored = cv2.applyColorMap(scaled, cv2.COLORMAP_TURBO)
        colored[invalid] = (0, 0, 0)

        out = self.bridge.cv2_to_imgmsg(colored, encoding='bgr8')
        out.header = msg.header
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = DepthColorizer()
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