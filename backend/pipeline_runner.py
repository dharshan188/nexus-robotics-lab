from typing import Dict, Any

from agents import PlannerAgent, BuilderAgent, ExecutorAgent
from behavior_agent import BehaviorAgent
from validator_agent import ValidatorAgent
from fix_agent import FixAgent


# =========================
# MAIN PIPELINE
# =========================

def run_pipeline(prompt: str) -> Dict[str, Any]:

    print("\n🔥 COPILOT START\n")

    planner = PlannerAgent()
    builder = BuilderAgent()
    executor = ExecutorAgent()
    validator = ValidatorAgent()
    fixer = FixAgent()
    behavior = BehaviorAgent()

    context: Dict[str, Any] = {}

    # =========================
    # STEP 1: PLAN
    # =========================
    plan = planner.plan(prompt)
    context["plan"] = plan

    # =========================
    # STEP 2: BUILD
    # =========================
    build = builder.build(prompt)

    if build.get("status") != "success":
        print("❌ Build failed")
        return {"status": "failed", "stage": "build"}

    workspace = build["workspace"]
    context["workspace"] = workspace

    print("WORKSPACE:", workspace)

    # =========================
    # STEP 3: EXECUTE
    # =========================
    launch_result = executor.launch(workspace)

    if launch_result.get("status") != "success":
        error = launch_result.get("reason", "launch_failed")
        print("❌ Launch failed:", error)
        return {
            "status": "failed",
            "stage": "launch",
            "error": error,
        }

    # =========================
    # STEP 4: VALIDATE + FIX LOOP
    # =========================
    for attempt in range(3):

        print(f"\n🔍 Validation attempt {attempt + 1}")

        result = validator.validate()

        if result.get("status") in {"success", "ok"}:
            print("✅ SYSTEM READY")

            # =========================
            # STEP 5: BEHAVIOR
            # =========================
            try:
                behavior.execute_behavior(plan)
            except Exception as e:
                print("[Behavior Error]", e)

            return {
                "status": "success",
                "attempts": attempt + 1
            }

        error = result.get("reason")
        print(f"❌ Error: {error}")

        # 🔥 FIX (CORRECTED)
        fixer.fix(workspace, error)

    # =========================
    # FINAL FAIL
    # =========================
    return {
        "status": "failed",
        "error": "validation_failed"
    }


# =========================
# API ENTRY
# =========================

def run_prompt(prompt: str) -> str:

    result = run_pipeline(prompt)

    if result.get("status") == "success":
        return "✅ Copilot completed successfully"

    return f"❌ Copilot failed: {result.get('error')}"


# =========================
# TEST
# =========================

if __name__ == "__main__":
    output = run_prompt("build robot with camera and move")
    print(output)