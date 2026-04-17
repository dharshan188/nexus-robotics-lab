from typing import Any, Dict, List

from skill_registry import run_skill
from validator_agent import ValidatorAgent
from fix_agent import FixAgent


Context = Dict[str, Any]


class PipelineExecutor:
    """Autonomous Copilot Execution Engine"""

    def execute(self, skills: List[str], context: Context) -> Context:

        shared_context = context if isinstance(context, dict) else {}

        shared_context.setdefault("requested_skills", list(skills or []))
        shared_context.setdefault("executed_skills", [])

        validator = ValidatorAgent()
        fixer = FixAgent()

        for skill_name in skills or []:

            print(f"\n🚀 Running skill: {skill_name}")

            try:
                shared_context = run_skill(skill_name, shared_context)
                shared_context["executed_skills"].append(skill_name)

            except Exception as e:
                print(f"❌ Skill failed: {e}")
                shared_context["error"] = str(e)
                shared_context = fixer.fix(shared_context)
                continue

            # =========================
            # VALIDATE AFTER EACH STEP
            # =========================
            validation = validator.validate()

            print(f"🔍 Validation: {validation}")

            if validation.get("status") != "success":

                shared_context["error"] = validation.get("reason", "unknown")

                print(f"⚠️ Error detected: {shared_context['error']}")

                shared_context = fixer.fix(shared_context)

                # retry same skill once
                try:
                    print(f"🔁 Retrying: {skill_name}")
                    shared_context = run_skill(skill_name, shared_context)
                except Exception as e:
                    print(f"❌ Retry failed: {e}")
                    continue

        print("\n✅ PIPELINE COMPLETE")

        return shared_context

    def run(self, skills: List[str], context: Context) -> Context:
        return self.execute(skills, context)