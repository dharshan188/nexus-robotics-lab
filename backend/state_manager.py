import threading
from datetime import datetime
from typing import Dict, Any, List


# =========================
# GLOBAL STATE
# =========================

_pipeline_lock = threading.Lock()

pipeline_status: Dict[str, Any] = {
    "stage": "idle",
    "agent": "",
    "message": "",
    "thinking": "",
    "current_task": "",
    "error": None,
    "fix": None,
    "history": [],
}


# =========================
# UPDATE STATUS
# =========================

def update_status(
    stage: str,
    agent: str,
    message: str,
    thinking: str = "",
    current_task: str = "",
    error: str | None = None,
    fix: Any = None,
):
    with _pipeline_lock:

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "agent": agent,
            "message": message,
            "thinking": thinking,
            "current_task": current_task,
            "error": error,
            "fix": fix,
        }

        pipeline_status.update(
            {
                "stage": stage,
                "agent": agent,
                "message": message,
                "thinking": thinking,
                "current_task": current_task,
                "error": error,
                "fix": fix,
            }
        )

        pipeline_status["history"].append(entry)

        print(f"[STATUS] {agent} → {message}")


# =========================
# GET STATUS
# =========================

def get_status() -> Dict[str, Any]:
    with _pipeline_lock:
        return dict(pipeline_status)


# =========================
# RESET
# =========================

def reset_status():
    with _pipeline_lock:
        pipeline_status.clear()
        pipeline_status.update(
            {
                "stage": "idle",
                "agent": "",
                "message": "",
                "thinking": "",
                "current_task": "",
                "error": None,
                "fix": None,
                "history": [],
            }
        )