import subprocess
import os
from typing import Dict, Any


# =========================
# UTILS
# =========================

def run(cmd: str):
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True
    )


def pip_install(package: str):
    print(f"[Dependency] Installing {package}...")
    run(f"pip install {package}")


# =========================
# DEPENDENCY AGENT
# =========================

class DependencyAgent:

    def resolve_dependencies(self, plan: dict) -> dict:
        result: Dict[str, Any] = {}

        try:
            safe_plan = plan if isinstance(plan, dict) else {}
            perception = safe_plan.get("perception", {})

            # =========================
            # YOLO (MODERN VERSION)
            # =========================
            if perception.get("model") == "yolo":
                print("🤖 YOLO required")

                # install ultralytics (YOLOv8)
                pip_install("ultralytics")
                pip_install("opencv-python")

                result["yolo"] = "ready"

            # =========================
            # ROS IMAGE BRIDGE (CAMERA)
            # =========================
            if perception:
                print("📷 Camera dependencies")

                run("sudo apt update")
                run("sudo apt install -y ros-humble-cv-bridge")

                result["cv_bridge"] = "ready"

            return result

        except Exception as e:
            print(f"[Dependency] Error: {e}")
            return result