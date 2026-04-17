import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/dharshan/nexus-robotics-lab/backend/ros2_ws/install/robot_pkg'
