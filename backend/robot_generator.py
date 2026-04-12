import os
import shutil
from pathlib import Path
from typing import Dict, Any


def _write_file(path: Path, content: str = "") -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")


def _package_xml() -> str:
	return """<?xml version=\"1.0\"?>
<package format=\"3\">
  <name>robot_pkg</name>
  <version>0.0.1</version>
  <description>Generated ROS2 robot package</description>
  <maintainer email=\"dev@example.com\">dev</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>

  <export>
	<build_type>ament_python</build_type>
  </export>
</package>
"""


def _setup_py() -> str:
	return """from setuptools import find_packages, setup

package_name = \"robot_pkg\"

setup(
	name=package_name,
	version=\"0.0.1\",
	packages=find_packages(exclude=[\"test\"]),
	data_files=[
		(\"share/ament_index/resource_index/packages\", [f\"resource/{package_name}\"]),
		(f\"share/{package_name}\", [\"package.xml\"]),
		(f\"share/{package_name}/launch\", [\"launch/simulation.launch.py\"]),
		(f\"share/{package_name}/urdf\", [\"urdf/robot.urdf\"]),
		(f\"share/{package_name}/worlds\", [\"worlds/empty.world\"]),
	],
	install_requires=[\"setuptools\"],
	zip_safe=True,
	maintainer=\"dev\",
	maintainer_email=\"dev@example.com\",
	description=\"Generated ROS2 robot package\",
	license=\"Apache-2.0\",
	tests_require=[\"pytest\"],
	entry_points={
		\"console_scripts\": [
			\"robot_node = robot_pkg.node:main\",
		],
	},
)
"""


def _node_py() -> str:
	return """import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotNode(Node):
	def __init__(self) -> None:
		super().__init__(\"robot_node\")
		self.publisher_ = self.create_publisher(String, \"/cmd_vel\", 10)
		self.timer = self.create_timer(1.0, self.publish_cmd)
		self.get_logger().info(\"Robot node started\")
		print(\"Robot node started\")

	def publish_cmd(self) -> None:
		msg = String()
		msg.data = \"forward\"
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
"""


def _simulation_launch() -> str:
	return """from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
	gazebo = ExecuteProcess(
		cmd=[\"gazebo\", \"--verbose\", \"empty.world\"],
		output=\"screen\",
	)

	spawn_placeholder = ExecuteProcess(
		cmd=[\"bash\", \"-c\", \"echo Spawning robot placeholder\"],
		output=\"screen\",
	)

	return LaunchDescription([
		gazebo,
		spawn_placeholder,
	])
"""


def _robot_urdf() -> str:
	return """<?xml version=\"1.0\"?>
<robot name=\"simple_robot\">
  <link name=\"base_link\">
	<visual>
	  <geometry>
		<box size=\"0.5 0.3 0.2\"/>
	  </geometry>
	  <material name=\"gray\"/>
	</visual>
	<collision>
	  <geometry>
		<box size=\"0.5 0.3 0.2\"/>
	  </geometry>
	</collision>
	<inertial>
	  <mass value=\"1.0\"/>
	  <inertia ixx=\"0.1\" ixy=\"0.0\" ixz=\"0.0\" iyy=\"0.1\" iyz=\"0.0\" izz=\"0.1\"/>
	</inertial>
  </link>
</robot>
"""


def _empty_world() -> str:
	return """<?xml version=\"1.0\" ?>
<sdf version=\"1.6\">
  <world name=\"default\">
	<include>
	  <uri>model://ground_plane</uri>
	</include>
	<include>
	  <uri>model://sun</uri>
	</include>
  </world>
</sdf>
"""


def create_ros2_workspace(config: dict) -> dict:
	"""Create a ROS2 workspace and basic Python robot package structure.

	Expected config format:
		{
			"robot_type": "4_wheel",
			"sensors": ["lidar", "camera"],
			"environment": "custom_map",
			"behavior": "navigation"
		}
	"""
	try:
		base_dir = Path(config.get("base_path") or os.getcwd()).resolve()
		workspace_dir = base_dir / "ros2_ws"
		src_dir = workspace_dir / "src"
		pkg_dir = src_dir / "robot_pkg"

		print("Creating workspace...")
		if workspace_dir.exists():
			shutil.rmtree(workspace_dir)
		src_dir.mkdir(parents=True, exist_ok=True)

		print("Creating package...")
		(pkg_dir / "robot_pkg").mkdir(parents=True, exist_ok=True)
		(pkg_dir / "launch").mkdir(parents=True, exist_ok=True)
		(pkg_dir / "urdf").mkdir(parents=True, exist_ok=True)
		(pkg_dir / "worlds").mkdir(parents=True, exist_ok=True)
		(pkg_dir / "resource").mkdir(parents=True, exist_ok=True)

		_write_file(pkg_dir / "package.xml", _package_xml())
		_write_file(pkg_dir / "setup.py", _setup_py())
		_write_file(pkg_dir / "robot_pkg" / "__init__.py", "")
		_write_file(pkg_dir / "robot_pkg" / "node.py", _node_py())
		_write_file(pkg_dir / "launch" / "simulation.launch.py", _simulation_launch())
		_write_file(pkg_dir / "urdf" / "robot.urdf", _robot_urdf())
		_write_file(pkg_dir / "worlds" / "empty.world", _empty_world())
		_write_file(pkg_dir / "resource" / "robot_pkg", "")

		print("Files generated...")
		return {
			"status": "success",
			"workspace_path": str(workspace_dir),
		}
	except Exception as exc:
		return {
			"status": "error",
			"workspace_path": "",
			"message": str(exc),
		}

