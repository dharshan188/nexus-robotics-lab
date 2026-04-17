from typing import Dict, Iterable, List


# =========================
# BASE
# =========================

def generate_base() -> str:
    return """  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.20" ixy="0.0" ixz="0.0"
               iyy="0.25" iyz="0.0"
               izz="0.30"/>
    </inertial>
  </link>"""


# =========================
# WHEELS (2-WHEEL DRIVE)
# =========================

def generate_wheels() -> str:
    return """
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.04"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.06" length="0.04"/>
      </geometry>
      <material name="black"/>
    </visual>
  </link>

  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.15 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.15 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
"""


# =========================
# LIDAR
# =========================

def generate_lidar() -> str:
    return """  <link name="lidar_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
      <material name="blue">
        <color rgba="0.1 0.1 0.8 1"/>
      </material>
    </visual>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0 0 0.15"/>
  </joint>"""


# =========================
# CAMERA
# =========================

def generate_camera() -> str:
    return """  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.08 0.04 0.04"/>
      </geometry>
      <material name="green">
        <color rgba="0.1 0.8 0.1 1"/>
      </material>
    </visual>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.15"/>
  </joint>

  <gazebo reference="camera_link">
    <sensor type="camera" name="camera">
      <update_rate>30</update_rate>
      <camera>
        <horizontal_fov>1.047</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
        </image>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <topicName>/camera/image_raw</topicName>
        <frameName>camera_link</frameName>
      </plugin>
    </sensor>
  </gazebo>
"""


# =========================
# SENSOR PARSER
# =========================

def _normalized_sensors(raw) -> List[str]:
    if not raw:
        return []

    if isinstance(raw, str):
        return [x.strip().lower() for x in raw.split(",")]

    if isinstance(raw, Iterable):
        return [str(x).strip().lower() for x in raw]

    return []


# =========================
# FINAL ASSEMBLY
# =========================

def assemble_robot(plan: Dict) -> str:

    sensors = _normalized_sensors(plan.get("sensors", []))

    parts = [
        generate_base(),
        generate_wheels()
    ]

    if "lidar" in sensors:
        parts.append(generate_lidar())

    if "camera" in sensors:
        parts.append(generate_camera())

    # 🚀 CRITICAL: DIFF DRIVE PLUGIN
    gazebo_plugin = """
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>0.3</wheel_separation>
      <wheel_diameter>0.12</wheel_diameter>
      <publish_odom>true</publish_odom>
    </plugin>
  </gazebo>
"""

    body = "\n".join(parts) + gazebo_plugin

    return f"""<?xml version="1.0"?>
<robot name="robot">
{body}
</robot>
"""