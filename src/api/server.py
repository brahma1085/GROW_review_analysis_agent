import asyncio
import sys
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import structlog
import os

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agent.orchestrator import create_agent
from src.config.manager import ConfigManager

logger = structlog.get_logger(__name__)

app = FastAPI(title="Groww Feedback Intelligence API")

# Allow requests from Vite frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in frontend_url.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for simple tracking
pipeline_status = {
    "status": "Idle",
    "last_run": "Never",
    "worker_id": "#08-HYD"
}

async def run_pipeline_task():
    global pipeline_status
    pipeline_status["status"] = "Running"
    try:
        config_path = str(project_root / "config.yaml")
        ConfigManager.load(config_path)
        config = ConfigManager.get_config()
        
        orchestrator = create_agent(config)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=config.collection.reporting_period_days)
        
        result = await orchestrator.run(start_date=start_date, end_date=end_date)
        
        pipeline_status["status"] = "Completed"
        pipeline_status["last_run"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.exception("Pipeline failed", error=str(e))
        pipeline_status["status"] = f"Failed: {str(e)}"

@app.get("/api/dashboard/summary")
async def get_summary():
    # In a real scenario, this would read from a database or JsonFileStore.
    # We return mocked data to populate the frontend for now.
    return {
        "health_score": 8.4,
        "health_score_delta": "+0.6 vs last week",
        "avg_star_rating": 4.2,
        "positive_sentiment": "68%",
        "total_reviews": "14.8k"
    }

@app.get("/api/dashboard/themes")
async def get_themes():
    # Mocked theme list based on UI design
    return [
        {
            "id": "1",
            "name": "Login/OTP Issues",
            "description": "Users are reporting delays in receiving OTPs during login.",
            "count": 450,
            "percentage": "12%",
            "priority": "CRITICAL",
        },
        {
            "id": "2",
            "name": "App Crash on Startup",
            "description": "App crashes immediately after opening for some users on older Android versions.",
            "count": 120,
            "percentage": "3%",
            "priority": "HIGH",
        }
    ]

@app.post("/api/admin/trigger-run")
async def trigger_run(background_tasks: BackgroundTasks):
    global pipeline_status
    if pipeline_status["status"] == "Running":
        return {"message": "Pipeline is already running."}
    
    background_tasks.add_task(run_pipeline_task)
    return {"message": "Pipeline started in the background."}

@app.get("/api/admin/status")
async def get_status():
    global pipeline_status
    return pipeline_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
