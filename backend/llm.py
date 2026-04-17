import json
import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")


# =========================
# DEFAULT STRUCTURE
# =========================

DEFAULT = {
    "action": "unknown",
    "robot_type": "ground",
    "sensors": [],
    "behavior": "none"
}


# =========================
# RULE FALLBACK
# =========================

def fallback(prompt: str) -> Dict[str, Any]:
    p = prompt.lower()

    out = DEFAULT.copy()

    if "drone" in p:
        out["robot_type"] = "drone"
    else:
        out["robot_type"] = "ground"

    if "camera" in p:
        out["sensors"].append("camera")

    if "lidar" in p:
        out["sensors"].append("lidar")

    if "move" in p:
        out["behavior"] = "move"

    if "follow" in p:
        out["behavior"] = "follow"

    out["action"] = "build_and_run"

    return out


# =========================
# LLM PARSER
# =========================

def parse_prompt(prompt: str) -> Dict[str, Any]:

    print("🧠 Parsing prompt:", prompt)

    if not GROK_API_KEY:
        print("⚠️ No API key → fallback")
        return fallback(prompt)

    payload = {
        "messages": [
            {
                "role": "system",
                "content": """You are a robotics copilot.

Return ONLY JSON in this format:

{
  "action": "build_and_run",
  "robot_type": "ground | drone",
  "sensors": ["camera", "lidar"],
  "behavior": "move | follow | patrol"
}
"""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    try:
        response = requests.post(
            GROK_API_URL,
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        result = json.loads(content)

        print("✅ LLM parsed:", result)
        return result

    except Exception as e:
        print("❌ LLM failed → fallback:", e)
        return fallback(prompt)