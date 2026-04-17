import os
import subprocess
import time
from typing import Dict, List

from planner import plan_robot
from robot_generator import create_ros2_workspace
from state import update_status


# =========================
# UTILS
# =========================

def run_cmd(cmd: str):
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True
    )


def is_gazebo_running() -> bool:
    result = run_cmd("pgrep -f gzserver")
    return result.stdout.strip() != ""


def has_robot_topics() -> bool:
    result = run_cmd("source /opt/ros/humble/setup.bash && ros2 topic list")
    return "/cmd_vel" in result.stdout


def kill_all():
    run_cmd("pkill -9 -f gazebo")
    run_cmd("pkill -9 -f ros2")


# =========================
# PLANNER
# =========================

class PlannerAgent:
    def plan(self, prompt: str) -> List[str]:
        update_status("planning", "PlannerAgent", "Analyzing prompt")
        skills = plan_robot(prompt)
        update_status("planning", "PlannerAgent", f"Plan: {skills}")
        return skills


# =========================
# BUILDER
# =========================

class BuilderAgent:

    def build(self, prompt: str) -> Dict:
        update_status("building", "BuilderAgent", "Creating workspace")

        result = create_ros2_workspace({"base_path": os.getcwd()})

        if result.get("status") != "success":
            return {"status": "error", "message": "workspace_failed"}

        workspace = result["workspace_path"]
        print("WORKSPACE:", workspace)

        build = run_cmd(f"cd {workspace} && colcon build")

        install_setup = os.path.join(workspace, "install/setup.bash")

        if build.returncode != 0 or not os.path.exists(install_setup):
            print(build.stderr)
            return {"status": "error", "message": "build_failed"}

        return {"status": "success", "workspace": workspace}


# =========================
# EXECUTOR (FIXED)
# =========================

class ExecutorAgent:

    def launch(self, workspace: str) -> Dict:
        update_status("executing", "ExecutorAgent", "Launching Gazebo")

        if not workspace:
            return {"status": "error", "reason": "workspace_missing"}

        install_setup = os.path.join(workspace, "install/setup.bash")

        if not os.path.exists(install_setup):
            return {"status": "error", "reason": "setup_missing"}

        if is_gazebo_running():
            print("⚠️ Gazebo already running")
            return {"status": "success"}

        cmd = [
            "bash",
            "-c",
            f"""
            unset PYTHONPATH;
            unset VIRTUAL_ENV;
            source /opt/ros/humble/setup.bash;
            source {install_setup};
            cd {workspace};
            ros2 launch robot_pkg simulation.launch.py
            """
        ]

        subprocess.Popen(cmd)

        print("🚀 Gazebo launching...")

        time.sleep(6)

        return {"status": "success"}


# =========================
# VALIDATOR
# =========================

class ValidatorAgent:

    def validate(self) -> Dict:
        update_status("validating", "ValidatorAgent", "Checking system")

        if not is_gazebo_running():
            return {"status": "error", "reason": "gazebo_not_running"}

        if not has_robot_topics():
            return {"status": "error", "reason": "robot_not_spawned"}

        return {"status": "success"}


# =========================
# FIX AGENT
# =========================

class FixAgent:

    def fix(self, workspace: str, reason: str) -> Dict:
        update_status("fixing", "FixAgent", f"Fixing: {reason}")

        kill_all()
        time.sleep(2)

        executor = ExecutorAgent()
        return executor.launch(workspace)


# =========================
# MAIN COPILOT
# =========================

class Copilot:

    def run(self, prompt: str) -> Dict:
        print("🔥 COPILOT START")

        planner = PlannerAgent()
        builder = BuilderAgent()
        executor = ExecutorAgent()
        validator = ValidatorAgent()
        fixer = FixAgent()

        # 1️⃣ PLAN
        planner.plan(prompt)

        # 2️⃣ BUILD
        build = builder.build(prompt)
        if build["status"] != "success":
            return build

        workspace = build["workspace"]

        # 3️⃣ EXECUTE
        executor.launch(workspace)

        # 4️⃣ VALIDATE + FIX LOOP
        for i in range(3):
            result = validator.validate()

            if result["status"] == "success":
                print("✅ SYSTEM WORKING")
                return {"status": "success"}

            print(f"❌ Attempt {i+1}: {result['reason']}")
            fixer.fix(workspace, result["reason"])

        return {"status": "failed"}