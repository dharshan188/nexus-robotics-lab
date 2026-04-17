import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

from validator_agent import ValidatorAgent


# =========================
# UTILS
# =========================

def run(cmd: str):
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True
    )


def log(context: Dict, cmd: str, result):
    context.setdefault("process_log", []).append(
        {
            "cmd": cmd,
            "returncode": result.returncode,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


# =========================
# FIX AGENT (FINAL)
# =========================

class FixAgent:

    def fix(self, workspace: str, error: str) -> Dict:

        print(f"[FixAgent] Fixing error: {error}")
        print("WORKSPACE:", workspace)

        context: Dict = {
            "workspace": workspace,
            "error": error,
            "process_log": []
        }

        workspace_path = Path(workspace).expanduser()
        validator = ValidatorAgent()

        max_retries = 3

        for attempt in range(1, max_retries + 1):

            print(f"\n[FixAgent] Attempt {attempt}")

            # =========================
            # STEP 1: KILL EVERYTHING
            # =========================
            for cmd in [
                "pkill -9 -f gazebo",
                "pkill -9 -f ros2"
            ]:
                res = run(cmd)
                log(context, cmd, res)

            time.sleep(2)

            # =========================
            # STEP 2: FIX STRATEGY
            # =========================
            if error in ["gazebo_not_running", "robot_not_spawned"]:
                fix_type = "relaunch"

            elif error == "build_failed":
                fix_type = "rebuild"

            else:
                fix_type = "relaunch"

            print(f"[FixAgent] Strategy: {fix_type}")

            # =========================
            # STEP 3: APPLY FIX
            # =========================
            if fix_type == "rebuild":
                res = run(f"cd {workspace} && colcon build")
                log(context, "colcon build", res)

            # =========================
            # STEP 4: ENSURE BUILD EXISTS
            # =========================
            install_setup = workspace_path / "install" / "setup.bash"

            if not install_setup.exists():
                print("[FixAgent] Missing install/setup.bash → rebuilding")

                res = run(f"cd {workspace} && colcon build")
                log(context, "colcon build", res)

                if not install_setup.exists():
                    print("❌ Build still broken")
                    error = "build_failed"
                    continue

            # =========================
            # STEP 5: RELAUNCH
            # =========================
            launch_cmd = f"""
            bash -c '
            unset PYTHONPATH;
            unset VIRTUAL_ENV;
            source /opt/ros/humble/setup.bash;
            cd {workspace};
            source {install_setup};
            ros2 launch robot_pkg simulation.launch.py
            '
            """

            subprocess.Popen(launch_cmd, shell=True, executable="/bin/bash")

            print("🚀 Relaunching Gazebo...")
            time.sleep(6)

            # =========================
            # STEP 6: VALIDATE
            # =========================
            validation = validator.validate()

            print("[FixAgent] Validation:", validation)

            if validation.get("status") in ["success", "ok"]:
                print("✅ FIX SUCCESS")

                return {
                    "status": "success",
                    "attempts": attempt
                }

            else:
                error = validation.get("reason", "unknown_error")
                print(f"❌ Still failing: {error}")

        # =========================
        # FINAL FAIL
        # =========================
        print("❌ Fix failed after retries")

        return {
            "status": "failed",
            "error": error
        }