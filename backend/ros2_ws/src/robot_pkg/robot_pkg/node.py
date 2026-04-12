import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotNode(Node):
	def __init__(self) -> None:
		super().__init__("robot_node")
		self.publisher_ = self.create_publisher(String, "/cmd_vel", 10)
		self.timer = self.create_timer(1.0, self.publish_cmd)
		self.get_logger().info("Robot node started")
		print("Robot node started")

	def publish_cmd(self) -> None:
		msg = String()
		msg.data = "forward"
		self.publisher_.publish(msg)


def main(args=None) -> None:
	rclpy.init(args=args)
	node = RobotNode()
	try:
		rclpy.spin(node)
	except KeyboardInterrupt:
		pass
	finally:
		node.destroy_node()
		rclpy.shutdown()
