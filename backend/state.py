import threading
from datetime import datetime
from typing import Dict, Any


# =========================
# GLOBAL STATE + LOCK
# =========================

_lock = threading.Lock()

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
    error=None,
    fix=None,
    thinking: str = "",
    current_task: str = "",
):
    with _lock:

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

        # CLEAN LOG (not full dump)
        print(f"[{agent}] {message}")


# =========================
# GET STATUS (SAFE COPY)
# =========================

def get_status() -> Dict[str, Any]:
    with _lock:
        return dict(pipeline_status)


# =========================
# RESET
# =========================

def reset_status():
    with _lock:
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