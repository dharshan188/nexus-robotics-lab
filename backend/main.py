import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from pipeline_runner import run_pipeline
from state import get_status, reset_status, update_status
from validator_agent import ValidatorAgent
from fix_agent import FixAgent


logger = logging.getLogger("ai_copilot_backend")
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="AI Robotics Copilot", version="1.0")


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# STATUS ENDPOINT
# =========================
@app.get("/status")
def status():
    return get_status()


# =========================
# MAIN COPILOT ENGINE
# =========================
@app.post("/generate")
async def generate(request: Request):

    try:
        reset_status()
        update_status("start", "System", "Pipeline request started")

        body = await request.json()
        prompt = (body or {}).get("prompt", "")

        print("\n🔥 PROMPT:", prompt)

        # =========================
        # STEP 1: RUN PIPELINE
        # =========================
        context = run_pipeline(prompt)

        # =========================
        # STEP 2: VALIDATION LOOP
        # =========================
        validator = ValidatorAgent()
        fixer = FixAgent()

        max_retries = 2

        for attempt in range(max_retries):

            validation = validator.validate()
            print("Validation:", validation)

            if validation.get("status") == "ok":
                update_status("success", "System", "Copilot completed successfully")
                return {
                    "status": "success",
                    "context": context,
                }

            # 🚨 AUTO FIX
            update_status(
                "fixing",
                "FixAgent",
                f"Fix attempt {attempt + 1}",
                error=validation.get("reason"),
            )

            context["error"] = validation.get("reason")
            context = fixer.fix(context)

        # =========================
        # FINAL FAILURE
        # =========================
        update_status("failure", "System", "Copilot failed after retries")

        return {
            "status": "error",
            "context": context,
            "reason": "Auto-fix failed",
        }

    except Exception as e:
        logger.exception("Unhandled error")

        update_status("failure", "System", "Unhandled error", error=str(e))

        return {
            "status": "error",
            "message": str(e),
        }


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)