import time
from typing import Any, Dict

try:
	import rclpy
	from geometry_msgs.msg import Twist
	from rclpy.node import Node
except Exception:
	rclpy = None
	Twist = None
	Node = None


class BehaviorAgent:
	def __init__(self) -> None:
		pass

	def move_forward(self, duration: float) -> None:
		if rclpy is None or Twist is None or Node is None:
			raise RuntimeError("ROS2 runtime not available (rclpy/geometry_msgs missing)")

		duration_seconds = max(0.0, float(duration))
		initialized_here = False
		node = None

		try:
			if not rclpy.ok():
				rclpy.init()
				initialized_here = True

			node = Node("behavior_agent")
			publisher = node.create_publisher(Twist, "/cmd_vel", 10)

			wait_deadline = time.monotonic() + 10.0
			while publisher.get_subscription_count() == 0 and time.monotonic() < wait_deadline:
				print("Waiting for /cmd_vel subscriber...")
				rclpy.spin_once(node, timeout_sec=0.0)
				time.sleep(0.5)

			if publisher.get_subscription_count() == 0:
				print("[BehaviorAgent] Error: no /cmd_vel subscriber found within 10 seconds")

			print("[BehaviorAgent] Waiting 1 second before publishing...")
			time.sleep(1.0)

			move_msg = Twist()
			move_msg.linear.x = 0.5
			move_msg.angular.z = 0.0

			print(f"[BehaviorAgent] Moving forward for {duration_seconds:.2f}s")
			end_time = time.monotonic() + duration_seconds
			while time.monotonic() < end_time:
				publisher.publish(move_msg)
				rclpy.spin_once(node, timeout_sec=0.0)
				time.sleep(0.1)

			stop_msg = Twist()
			stop_msg.linear.x = 0.0
			stop_msg.angular.z = 0.0
			publisher.publish(stop_msg)
			rclpy.spin_once(node, timeout_sec=0.0)
			print("[BehaviorAgent] Robot stopped")
		finally:
			if node is not None:
				node.destroy_node()
			if initialized_here and rclpy.ok():
				rclpy.shutdown()

	def execute_behavior(self, plan: Dict[str, Any]) -> None:
		duration = 5.0
		if isinstance(plan, dict):
			tasks = plan.get("tasks", [])
			if isinstance(tasks, list):
				for task in tasks:
					if isinstance(task, dict) and str(task.get("type", "")).strip().lower() == "move":
						duration = float(task.get("duration", duration))
						break

		try:
			self.move_forward(duration)
		except Exception as exc:
			print(f"[BehaviorAgent] Error: {exc}")

