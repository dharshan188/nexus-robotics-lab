import os
import json
import logging
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv


load_dotenv()  # load .env if present

# Read Grok API configuration from environment (safe defaults)
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")

logger = logging.getLogger("ai_copilot_llm")
if not logger.handlers:
    # Minimal safe logging configuration for module usage
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


DEFAULT_OUTPUT = {
    "action": "unknown",
    "robot_type": "",
    "sensors": [],
    "environment": "",
    "behavior": "",
}


def _rule_based_parse(prompt: str) -> Dict[str, Any]:
    p = prompt.lower()
    out = DEFAULT_OUTPUT.copy()

    # Intent detection rules
    if any(kw in p for kw in ("open gazebo", "start gazebo", "launch gazebo", "open simulator")):
        out["action"] = "open_gazebo"
    elif any(kw in p for kw in ("create", "build", "robot", "car", "drone")):
        out["action"] = "generate_robot"
    else:
        out["action"] = "unknown"

    # robot type heuristics
    if "drone" in p or "quadcopter" in p:
        out["robot_type"] = "drone"
    elif "car" in p or "rover" in p:
        out["robot_type"] = "wheeled"
    elif "arm" in p or "manipulator" in p:
        out["robot_type"] = "manipulator"
    else:
        out["robot_type"] = ""

    # sensors heuristics
    sensors: List[str] = []
    for s in ("lidar", "camera", "imu", "gps", "sonar", "depth camera", "camera"):
        if s in p:
            sensors.append(s)
    out["sensors"] = sensors

    # environment heuristics
    if "gazebo" in p or "simulator" in p or "simulation" in p:
        out["environment"] = "simulation"
    elif "indoor" in p:
        out["environment"] = "indoor"
    elif "outdoor" in p:
        out["environment"] = "outdoor"
    else:
        out["environment"] = ""

    # behavior heuristics
    if any(w in p for w in ("patrol", "survey", "explore")):
        out["behavior"] = "patrol"
    elif any(w in p for w in ("follow", "track")):
        out["behavior"] = "follow"
    elif any(w in p for w in ("navigate", "go to", "move to")):
        out["behavior"] = "navigate"
    else:
        out["behavior"] = ""

    return out


def _safe_extract_json(text: str) -> Any:
    """Attempt to extract the first JSON object from text.

    Returns parsed JSON or raises ValueError.
    """
    text = text.strip()
    # Quick attempt: direct json parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fallback: find the first { ... } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON snippet: {e}")

    raise ValueError("No JSON object found in text")


def parse_prompt(prompt: str) -> Dict[str, Any]:
    """Parse a natural language robotics command into structured JSON.

    Tries to use the Grok API when an API key is available. If the API
    call fails or returns invalid JSON, falls back to a rule-based parser.

    The returned dict always contains the keys: action, robot_type, sensors,
    environment, behavior.
    """
    logger.info("parse_prompt input: %s", prompt)

    # Prepare a safe default to return in all error cases
    safe_default = DEFAULT_OUTPUT.copy()

    # First, detect simple intent via rules (we will log this)
    detected = _rule_based_parse(prompt)
    logger.info("Rule-based detected action: %s", detected.get("action"))

    # Try Grok API if configured
    if not GROK_API_KEY:
        # explicit, user-facing warning and fallback
        print("GROK API key not found, using fallback parser")
        logger.info("GROK_API_KEY not set; using rule-based fallback")
        print(f"Input prompt: {prompt}")
        print(f"Detected action (rules): {detected.get('action')}")
        print(f"Output: {json.dumps(detected)}")
        return detected

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {"role": "system", "content": "Convert robotics instructions into structured JSON"},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 800,
        "temperature": 0,
    }

    try:
        resp = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=10)
    except Exception as e:
        logger.exception("Grok API request failed: %s", e)
        logger.info("Falling back to rule-based parser")
        print(f"Input prompt: {prompt}")
        print(f"Detected action (rules): {detected.get('action')}")
        print(f"Output: {json.dumps(detected)}")
        return detected

    if resp.status_code != 200:
        logger.warning("Grok API returned non-200: %s %s", resp.status_code, resp.text[:200])
        logger.info("Falling back to rule-based parser")
        print(f"Input prompt: {prompt}")
        print(f"Detected action (rules): {detected.get('action')}")
        print(f"Output: {json.dumps(detected)}")
        return detected

    # Attempt to parse the response safely
    try:
        # Common API shapes: direct JSON or nested content field
        content = None
        try:
            body = resp.json()
        except ValueError:
            # not JSON, try to extract JSON from text
            body = None

        if isinstance(body, dict):
            # try common fields
            if "json" in body and isinstance(body["json"], dict):
                content = body["json"]
            elif "content" in body and isinstance(body["content"], str):
                try:
                    content = _safe_extract_json(body["content"])
                except Exception:
                    # content field may already be a dict
                    content = body["content"]
            elif "choices" in body and isinstance(body["choices"], list) and body["choices"]:
                # many LLM APIs put text in choices[0].text or message
                first = body["choices"][0]
                if isinstance(first, dict):
                    txt = first.get("text") or first.get("message") or first.get("content")
                    if isinstance(txt, str):
                        content = _safe_extract_json(txt)
            else:
                # body might already be the structured dict we want
                content = body

        if content is None:
            # attempt to parse raw text
            text = resp.text
            content = _safe_extract_json(text)

        # Validate that content is a dict with expected keys
        if not isinstance(content, dict):
            raise ValueError("Parsed content is not a JSON object")

        # Ensure required keys exist, otherwise merge with rule-based values
        result = {
            "action": content.get("action") or detected.get("action") or safe_default["action"],
            "robot_type": content.get("robot_type") or detected.get("robot_type") or safe_default["robot_type"],
            "sensors": content.get("sensors") if isinstance(content.get("sensors"), list) else detected.get("sensors") or safe_default["sensors"],
            "environment": content.get("environment") or detected.get("environment") or safe_default["environment"],
            "behavior": content.get("behavior") or detected.get("behavior") or safe_default["behavior"],
        }

        logger.info("Grok parsing successful; final action: %s", result.get("action"))
        print(f"Input prompt: {prompt}")
        print(f"Detected action (rules): {detected.get('action')}")
        print(f"Output: {json.dumps(result)}")
        return result

    except Exception as e:
        logger.exception("Failed to parse Grok response: %s", e)
        logger.info("Using rule-based fallback result")
        print(f"Input prompt: {prompt}")
        print(f"Detected action (rules): {detected.get('action')}")
        print(f"Output: {json.dumps(detected)}")
        return detected


if __name__ == "__main__":
    # Quick manual smoke test
    sample = "Create a drone with LiDAR and camera for outdoor patrol in Gazebo"
    out = parse_prompt(sample)
    print(json.dumps(out, indent=2))
