from robot_generator import create_ros2_workspace

config = {
    "robot_type": "4_wheel",
    "sensors": ["lidar"],
    "environment": "empty",
    "behavior": "none"
}

result = create_ros2_workspace(config)
print(result)