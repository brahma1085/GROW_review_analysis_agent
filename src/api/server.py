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
from src.delivery.mcp_client import MCPClient
import json
import glob

logger = structlog.get_logger(__name__)

app = FastAPI(title="Groww Feedback Intelligence API")

# Allow requests from Vite frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:3000,https://growagent-six.vercel.app")
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

def get_latest_aggregate():
    search_path = str(project_root / "data" / "aggregates" / "com.nextbillion.groww" / "*_aggregate.json")
    files = glob.glob(search_path)
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, "r") as f:
        return json.load(f)

@app.get("/api/dashboard/summary")
async def get_summary():
    agg = get_latest_aggregate()
    if not agg:
        return {
            "health_score": 0,
            "health_score_delta": "No data",
            "avg_star_rating": 0,
            "positive_sentiment": "0%",
            "total_reviews": "0",
            "negative_reviews": 0,
            "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0}
        }
    
    metrics = agg.get("metrics", {})
    avg_star = round(metrics.get("avg_star_rating", 0), 1)
    
    sentiment_dist = metrics.get("sentiment_distribution", {})
    pct = sentiment_dist.get("percentages", {})
    positive_pct = pct.get("positive", 0)
    
    health_score = round((positive_pct / 100.0) * 5 + (avg_star / 5) * 5, 1)
    
    return {
        "health_score": health_score,
        "health_score_delta": "",
        "avg_star_rating": avg_star,
        "positive_sentiment": f"{round(positive_pct, 1)}%",
        "total_reviews": str(metrics.get("reviews_analyzed", 0)),
        "negative_reviews": sentiment_dist.get("negative_count", 0),
        "sentiment_breakdown": {
            "positive": round(pct.get("positive", 0), 1),
            "neutral": round(pct.get("neutral", 0), 1),
            "negative": round(pct.get("negative", 0), 1)
        }
    }

@app.get("/api/dashboard/themes")
async def get_themes():
    agg = get_latest_aggregate()
    if not agg:
        return []
    
    mapped_themes = []
    for t in agg.get("themes", []):
        theme_data = t.get("theme", {})
        mapped_themes.append({
            "id": theme_data.get("id", ""),
            "name": theme_data.get("name", "Unknown Theme"),
            "description": theme_data.get("description", ""),
            "count": theme_data.get("review_count", 0),
            "percentage": f"{round(theme_data.get('review_percentage', 0), 1)}%",
            "priority": str(t.get("priority", "low")).upper()
        })
    
    # Sort by count descending
    mapped_themes.sort(key=lambda x: x["count"], reverse=True)
    return mapped_themes

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

@app.post("/api/admin/test-mcp")
async def test_mcp():
    try:
        config_path = str(project_root / "config.yaml")
        ConfigManager.load(config_path)
        config = ConfigManager.get_config()
        
        mcp_client = MCPClient()
        
        test_pulse = {
            "app_id": "com.nextbillion.groww",
            "period_start": datetime.now().isoformat(),
            "period_end": datetime.now().isoformat(),
            "metrics": {},
            "themes": [{"theme": {"name": "Test Theme", "description": "This is a test from the MCP test endpoint."}}]
        }
        
        # Test Docs
        if config.delivery.google_docs.document_id:
            await mcp_client.deliver_via_docs(
                document_id=config.delivery.google_docs.document_id,
                title="Test Pulse - Google Docs",
                pulse_markdown="# Test Pulse\nThis is a test from the MCP test endpoint."
            )
        
        # Test Email
        if config.delivery.gmail.recipients:
            await mcp_client.deliver_via_email(
                recipients=config.delivery.gmail.recipients,
                subject="Test Pulse - Gmail",
                pulse_markdown="# Test Pulse\nThis is a test from the MCP test endpoint.",
                is_html=False
            )
        
        return {"status": "success", "message": "Successfully sent test pulse to Google Docs and Gmail via MCP!"}
    except Exception as e:
        logger.error(f"MCP Test Failed: {str(e)}")
        return {"status": "error", "message": f"MCP Test Failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
