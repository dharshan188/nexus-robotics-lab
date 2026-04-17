import subprocess
import datetime
import os
from typing import Dict


LOG_FILE = os.path.expanduser("~/nexus-robotics-lab/backend/system.log")


# =========================
# WRITE LOG
# =========================

def write_log(content: str):
    with open(LOG_FILE, "w") as f:  # overwrite each run
        f.write(content)


# =========================
# ERROR PARSER
# =========================

def parse_error(stderr: str) -> str:
    if not stderr:
        return ""

    err = stderr.lower()

    if "no module named" in err:
        return "module_missing"

    if "joint" in err and "not found" in err:
        return "urdf_error"

    if "spawn_entity" in err:
        return "spawn_failed"

    if "colcon" in err:
        return "build_failed"

    return "unknown"


# =========================
# RUN + LOG
# =========================

def run_and_log(cmd: str) -> Dict:
    try:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=60
        )

        error_type = parse_error(result.stderr)

        log_content = f"""
===== TIMESTAMP =====
{datetime.datetime.now()}

===== COMMAND =====
{cmd}

===== STDOUT =====
{result.stdout}

===== STDERR =====
{result.stderr}

===== ERROR TYPE =====
{error_type}
"""

        write_log(log_content)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error_type": error_type
        }

    except Exception as e:
        error_msg = str(e)

        write_log(f"""
===== ERROR =====
{error_msg}
""")

        return {
            "success": False,
            "stderr": error_msg,
            "error_type": "execution_failed"
        }