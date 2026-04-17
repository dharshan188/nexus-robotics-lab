import subprocess
import time
from typing import Dict


class ValidatorAgent:

    def _run(self, cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            check=False,
        )

    # =========================
    # 1. GAZEBO CHECK
    # =========================
    def _is_gazebo_running(self) -> bool:
        result = self._run("pgrep -f gzserver")
        return bool(result.stdout.strip())

    # =========================
    # 2. SPAWN SERVICE CHECK
    # =========================
    def _spawn_service_available(self) -> bool:
        result = self._run(
            "source /opt/ros/humble/setup.bash && ros2 service list"
        )
        return "/spawn_entity" in result.stdout

    # =========================
    # 3. ROBOT EXISTS IN WORLD
    # =========================
    def _robot_exists(self) -> bool:
        for _ in range(5):
            result = self._run(
                "source /opt/ros/humble/setup.bash && "
                "ros2 service call /get_model_list gazebo_msgs/srv/GetModelList"
            )
            if "robot" in result.stdout or "my_robot" in result.stdout:
                return True
            time.sleep(1)
        return False

    # =========================
    # 4. CMD_VEL CONNECTED
    # =========================
    def _cmd_vel_active(self) -> bool:
        result = self._run(
            "source /opt/ros/humble/setup.bash && ros2 topic info /cmd_vel"
        )
        return "Publisher count" in result.stdout

    # =========================
    # 5. ODOM ACTIVE
    # =========================
    def _odom_active(self) -> bool:
        result = self._run(
            "source /opt/ros/humble/setup.bash && ros2 topic echo /odom --once"
        )
        return "pose" in result.stdout.lower()

    # =========================
    # MAIN VALIDATE
    # =========================
    def validate(self) -> Dict[str, str]:

        # 1. Gazebo
        if not self._is_gazebo_running():
            return {"status": "error", "reason": "gazebo_not_running"}

        # 2. Spawn service
        if not self._spawn_service_available():
            return {"status": "error", "reason": "spawn_service_missing"}

        # 3. Robot existence
        if not self._robot_exists():
            return {"status": "error", "reason": "robot_not_spawned"}

        # 4. cmd_vel active
        if not self._cmd_vel_active():
            return {"status": "error", "reason": "cmd_vel_inactive"}

        # 5. odom active
        if not self._odom_active():
            return {"status": "error", "reason": "odom_not_publishing"}

        return {"status": "ok", "reason": "robot_fully_operational"}