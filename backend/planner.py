from typing import List, Dict, Any
from llm import parse_prompt


# =========================
# PLANNER
# =========================

def plan_robot(prompt: str) -> List[str]:
    """
    Convert prompt into ordered skill pipeline
    """

    try:
        parsed: Dict[str, Any] = parse_prompt(prompt)

        print("🧠 Parsed prompt:", parsed)

        skills: List[str] = []

        action = parsed.get("action", "")
        robot_type = parsed.get("robot_type", "ground")
        sensors = parsed.get("sensors", [])
        behavior = parsed.get("behavior", "")

        # =========================
        # CORE BUILD
        # =========================
        if action in ("build_and_run", "generate_robot"):

            if robot_type == "drone":
                skills.append("build_drone")
            else:
                skills.append("build_ground_robot")

            skills.append("launch_simulation")

        # =========================
        # SENSORS
        # =========================
        if "camera" in sensors:
            skills.append("add_camera")

        if "lidar" in sensors:
            skills.append("add_lidar")

        # =========================
        # HUMAN INTERACTION
        # =========================
        if behavior in ("follow", "detect"):
            skills.append("spawn_human")

        # =========================
        # BEHAVIOR
        # =========================
        if behavior == "move":
            skills.append("move_forward")

        elif behavior == "follow":
            skills.append("follow_human")

        elif behavior == "patrol":
            skills.append("patrol")

        # =========================
        # CLEANUP DUPLICATES
        # =========================
        skills = list(dict.fromkeys(skills))

        print("📋 Final Plan:", skills)

        return skills

    except Exception as e:
        print(f"❌ Planner error: {e}")
        return []