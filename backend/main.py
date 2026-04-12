from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from llm import parse_prompt
import subprocess
import logging


logger = logging.getLogger("ai_copilot_backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


app = FastAPI(title="AI Robotics Copilot", version="0.1")

# Enable CORS for all origins (development-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate")
async def generate(request: Request):
    """Accept a JSON body with `prompt`, parse it via imported `parse_prompt`,
    execute supported actions and return JSON responses. Entire handler is
    defensive: it never allows uncaught exceptions to crash the server.
    """
    try:
        try:
            body = await request.json()
        except Exception:
            logger.exception("Failed to parse request JSON")
            return {"status": "error", "message": "Invalid JSON input"}

        prompt = (body or {}).get("prompt", "")
        print("🔥 API HIT")
        print("Prompt received:", prompt)

        # Use the parser from llm.py
        parsed = parse_prompt(prompt)
        print("Parsed output:", parsed)

        action = parsed.get("action")

        if action == "open_gazebo":
            print("Launching Gazebo...")
            try:
                subprocess.Popen(
                    ["bash", "-c", "source /opt/ros/humble/setup.bash && gazebo"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                logger.exception("Gazebo launch failed: executable not found")
                return {"status": "error", "message": "Gazebo not installed or ROS2 not sourced"}
            except Exception as e:
                logger.exception("Unexpected error launching Gazebo: %s", e)
                return {"status": "error", "message": str(e)}

            return {"status": "success", "message": "Gazebo launched"}

        elif action == "generate_robot":
            return {"status": "success", "data": parsed}

        else:
            return {"status": "error", "message": "Unknown command"}

    except Exception as e:
        logger.exception("Unhandled error in /generate: %s", e)
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting AI Robotics Copilot backend (development server)")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
