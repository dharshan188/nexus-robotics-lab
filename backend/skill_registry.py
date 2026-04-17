import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Callable

from logger import run_and_log

Context = Dict[str, Any]
Skill = Callable[[Context], Context]


# =========================
# HELPERS
# =========================

def _run(cmd: str, workspace: Path | None = None):
  ws = workspace or Path("~/nexus-robotics-lab/backend/ros2_ws").expanduser()
  install_setup = ws / "install/setup.bash"
  return run_and_log(
    "unset PYTHONPATH && "
    "unset VIRTUAL_ENV && "
    "source /opt/ros/humble/setup.bash && "
    f"source {install_setup} && "
    + cmd
  )


# =========================
# BUILD ROBOT
# =========================

def build_ground_robot(context: Context) -> Context:

    ws = Path("~/nexus-robotics-lab/backend/ros2_ws").expanduser()
    pkg = ws / "src/robot_pkg"
    urdf = pkg / "urdf/robot.urdf"
    launch = pkg / "launch/simulation.launch.py"

    (pkg / "urdf").mkdir(parents=True, exist_ok=True)
    (pkg / "launch").mkdir(parents=True, exist_ok=True)

    # -------- URDF (WORKING) --------
    urdf.write_text("""<?xml version="1.0"?>
<robot name="robot">

<link name="base_link">
  <visual><geometry><box size="0.4 0.3 0.1"/></geometry></visual>
  <collision><geometry><box size="0.4 0.3 0.1"/></geometry></collision>
  <inertial>
    <mass value="2"/>
    <inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0"/>
  </inertial>
</link>

<link name="left_wheel">
  <visual><geometry><cylinder radius="0.05" length="0.02"/></geometry></visual>
</link>

<link name="right_wheel">
  <visual><geometry><cylinder radius="0.05" length="0.02"/></geometry></visual>
</link>

<joint name="left_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="left_wheel"/>
  <origin xyz="0 0.15 0"/>
</joint>

<joint name="right_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="right_wheel"/>
  <origin xyz="0 -0.15 0"/>
</joint>

<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.3</wheel_separation>
    <wheel_diameter>0.1</wheel_diameter>
    <publish_odom>true</publish_odom>
  </plugin>
</gazebo>

</robot>
""")

    # -------- LAUNCH --------
    launch.write_text("""from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg = get_package_share_directory('robot_pkg')
    urdf = os.path.join(pkg, 'urdf', 'robot.urdf')

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'robot', '-file', urdf],
            output='screen'
        ),
    ])
""")

    # BUILD
    build_result = _run(f"cd {ws} && colcon build", workspace=ws)

    install_setup = ws / "install/setup.bash"
    print(f"[build_ground_robot] workspace: {ws}")
    print(f"[build_ground_robot] install/setup.bash exists: {install_setup.exists()}")

    if (not build_result.get("success")) or (not install_setup.exists()):
        raise RuntimeError("build_failed")

    context["workspace"] = str(ws)
    context["workspace_path"] = str(ws)
    print("✅ Robot built")

    return context


# =========================
# LAUNCH SIMULATION
# =========================

def launch_simulation(context: Context) -> Context:

    ws = Path(context.get("workspace_path") or context.get("workspace") or "~/nexus-robotics-lab/backend/ros2_ws").expanduser()
    install_setup = ws / "install/setup.bash"

    print(f"[launch_simulation] workspace: {ws}")
    print(f"[launch_simulation] install/setup.bash exists: {install_setup.exists()}")

    if not install_setup.exists():
        raise RuntimeError("build_failed")

    _run(f"cd {ws} && ros2 launch robot_pkg simulation.launch.py", workspace=ws)

    time.sleep(5)

    print("🚀 Simulation launched")
    context["simulation"] = True
    return context


# =========================
# MOVE ROBOT
# =========================

def move_forward(context: Context) -> Context:

    _run(
        "ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "
        "'{linear: {x: 0.5}, angular: {z: 0.0}}'"
    )

    time.sleep(3)

    _run(
        "ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "
        "'{linear: {x: 0.0}, angular: {z: 0.0}}'"
    )

    print("➡️ Robot moved")
    return context


# =========================
# SPAWN HUMAN
# =========================

def spawn_human(context: Context) -> Context:

    human_sdf = Path("~/nexus-robotics-lab/backend/human.sdf").expanduser()

    if not human_sdf.exists():
        human_sdf.write_text("""<?xml version="1.0"?>
<sdf version="1.6">
  <model name="human">
    <link name="link">
      <visual name="visual">
        <geometry>
          <box><size>0.5 0.5 1.7</size></box>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
""")

    _run(f"ros2 run gazebo_ros spawn_entity.py -entity human -file {human_sdf}")

    print("🧍 Human spawned")
    return context


# =========================
# SKILL REGISTRY
# =========================

SKILLS: Dict[str, Skill] = {
    "build_ground_robot": build_ground_robot,
    "launch_simulation": launch_simulation,
    "move_forward": move_forward,
    "spawn_human": spawn_human,
}


def run_skill(name: str, context: Context) -> Context:
    if name not in SKILLS:
        raise ValueError(f"Skill not found: {name}")

    print(f"\n🔥 Running skill: {name}")
    return SKILLS[name](context)