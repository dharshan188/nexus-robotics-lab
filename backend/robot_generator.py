import os
import shutil
from pathlib import Path

from templates import assemble_robot


# =========================
# FILE WRITER
# =========================

def _write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write(content)


# =========================
# PACKAGE.XML
# =========================

def _package_xml() -> str:
    return """<?xml version="1.0"?>
<package format="3">
  <name>robot_pkg</name>
  <version>0.0.1</version>
  <description>Generated ROS2 robot package</description>

  <maintainer email="dev@example.com">dev</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>gazebo_ros</exec_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
"""


# =========================
# SETUP.PY
# =========================

def _setup_py() -> str:
    return """from setuptools import find_packages, setup

package_name = "robot_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/simulation.launch.py"]),
        (f"share/{package_name}/urdf", ["urdf/robot.urdf", "urdf/human.urdf"]),
        (f"share/{package_name}/worlds", ["worlds/empty.world"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dev",
    maintainer_email="dev@example.com",
    description="Generated ROS2 robot package",
    license="Apache-2.0",
)
"""


# =========================
# LAUNCH FILE (FIXED)
# =========================

def _simulation_launch() -> str:
    return """from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_path = get_package_share_directory('robot_pkg')
    robot_urdf = os.path.join(pkg_path, 'urdf', 'robot.urdf')

    return LaunchDescription([

        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'my_robot',
                '-file', robot_urdf
            ],
            output='screen'
        ),
    ])
"""


# =========================
# EMPTY WORLD
# =========================

def _empty_world() -> str:
    return """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>
  </world>
</sdf>
"""


# =========================
# HUMAN (SIMPLE)
# =========================

def _human_urdf() -> str:
    return """<?xml version="1.0"?>
<robot name="human">
    <link name="human">
        <visual>
            <geometry>
                <box size="0.5 0.5 1.7"/>
            </geometry>
            <material name="blue">
                <color rgba="0.1 0.1 0.8 1"/>
            </material>
        </visual>
    </link>
</robot>
"""


# =========================
# MAIN GENERATOR
# =========================

def create_ros2_workspace(config: dict) -> dict:
    try:
        base_dir = Path(config.get("base_path") or os.getcwd()).resolve()
        workspace_dir = base_dir / "ros2_ws"
        src_dir = workspace_dir / "src"
        pkg_dir = src_dir / "robot_pkg"

        print("📦 Creating workspace...")

        # CLEAN OLD
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)

        # CREATE STRUCTURE
        (pkg_dir / "robot_pkg").mkdir(parents=True, exist_ok=True)
        (pkg_dir / "launch").mkdir(parents=True, exist_ok=True)
        (pkg_dir / "urdf").mkdir(parents=True, exist_ok=True)
        (pkg_dir / "worlds").mkdir(parents=True, exist_ok=True)
        (pkg_dir / "resource").mkdir(parents=True, exist_ok=True)

        # WRITE FILES
        _write_file(pkg_dir / "package.xml", _package_xml())
        _write_file(pkg_dir / "setup.py", _setup_py())
        _write_file(pkg_dir / "robot_pkg" / "__init__.py", "")

        print("🚀 Writing launch file...")
        _write_file(pkg_dir / "launch" / "simulation.launch.py", _simulation_launch())

        print("🤖 Generating robot URDF...")
        robot_urdf = assemble_robot(config)  # must include diff drive plugin
        _write_file(pkg_dir / "urdf" / "robot.urdf", robot_urdf)

        print("🧍 Adding human...")
        _write_file(pkg_dir / "urdf" / "human.urdf", _human_urdf())

        print("🌍 Adding world...")
        _write_file(pkg_dir / "worlds" / "empty.world", _empty_world())

        _write_file(pkg_dir / "resource" / "robot_pkg", "")

        print("✅ Workspace ready")

        return {
            "status": "success",
            "workspace_path": str(workspace_dir),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "workspace_path": "",
        }