import json
import os
from typing import Any, Dict

requests = None
try:
    import requests
except Exception:
    requests = None


GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")


# =========================
# LLM FIX (STRUCTURED)
# =========================

def llm_fix(error_log: str, context: str) -> Dict:
    print("🤖 Using LLM to fix error...")

    if not GROK_API_KEY or requests is None:
        return {
            "type": "manual",
            "message": "LLM unavailable"
        }

    prompt = f"""
You are a ROS2 debugging AI.

Return ONLY JSON.

Error:
{error_log}

Context:
{context}

Output format:
{{
  "type": "install_package | rebuild | fix_urdf | relaunch | unknown",
  "value": "string",
  "file": "optional path"
}}
"""

    try:
        response = requests.post(
            GROK_API_URL,
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            },
            timeout=20
        )

        data: Any = response.json()

        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as e:
        return {
            "type": "unknown",
            "message": str(e)
        }


# =========================
# RULE-BASED FIX
# =========================

def fix_error(error_log: str, context: str = "") -> Dict:
    print("🔍 Analyzing error...")

    if not error_log:
        return {"type": "none"}

    log = error_log.lower()

    # 🔥 COMMON ERRORS

    if "modulenotfounderror" in log:
        return {
            "type": "install_package",
            "value": extract_module(error_log)
        }

    if "package not found" in log:
        return {
            "type": "source_workspace"
        }

    if "colcon build failed" in log:
        return {
            "type": "clean_build"
        }

    if "joint" in log and "not found" in log:
        return {
            "type": "fix_urdf",
            "message": "Joint mismatch in URDF"
        }

    # fallback to LLM
    return llm_fix(error_log, context)


# =========================
# HELPERS
# =========================

def extract_module(error_log: str) -> str:
    import re
    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_log)
    return match.group(1) if match else ""