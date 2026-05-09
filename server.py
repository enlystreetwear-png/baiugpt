# server.py

from fastapi import FastAPI, Header, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import AI functions from core.model
from core.model import (
    generate_weekly_plan,
    generate_analysis,
    analyze_channel,
    chat_with_coach,
    estimate_goal_timeline,
    generate_task_guide
)

# -------------------------
# API Key Configuration
# -------------------------
API_KEY = "baiu-secret-12345"

def validate_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# -------------------------
# Request Models
# -------------------------
class WeeklyPlanRequest(BaseModel):
    channel: Optional[Dict[str, Any]] = {}
    profile: Optional[Dict[str, Any]] = {}
    snapshots: Optional[List[Dict[str, Any]]] = []

class AnalysisRequest(BaseModel):
    channel: Optional[Dict[str, Any]] = {}
    profile: Optional[Dict[str, Any]] = {}
    snapshots: Optional[List[Dict[str, Any]]] = []

class AnalyzeChannelRequest(BaseModel):
    channel: Optional[Dict[str, Any]] = {}
    videos: Optional[List[Dict[str, Any]]] = []

class CoachRequest(BaseModel):
    messages: Optional[List[Dict[str, Any]]] = []
    user: Optional[Dict[str, Any]] = {}
    channel: Optional[Dict[str, Any]] = {}
    profile: Optional[Dict[str, Any]] = {}
    taskContext: Optional[Dict[str, Any]] = None
    niche: Optional[str] = None
    lang: Optional[str] = None

class GoalRoadmapRequest(BaseModel):
    channel: Optional[Dict[str, Any]] = {}
    profile: Optional[Dict[str, Any]] = {}
    snapshots: Optional[List[Dict[str, Any]]] = []

class TaskGuideRequest(BaseModel):
    task: Dict[str, Any]
    channel: Optional[Dict[str, Any]] = {}
    profile: Optional[Dict[str, Any]] = {}

# -------------------------
# FastAPI Setup
# -------------------------
app = FastAPI(title="BaiuGPT API", version="0.1.0")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "name": "BaiuGPT"}

# -------------------------
# Weekly Plan Endpoint
# -------------------------
@app.post("/ai/weekly-plan")
def weekly_plan(request: WeeklyPlanRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return generate_weekly_plan(request.dict())
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Analysis Endpoint
# -------------------------
@app.post("/ai/analysis")
def analysis(request: AnalysisRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return generate_analysis(request.dict())
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Analyze Channel Endpoint
# -------------------------
@app.post("/ai/analyze-channel")
def analyze_channel_route(request: AnalyzeChannelRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return analyze_channel(request.dict())
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# AI Coach Endpoint
# -------------------------
@app.post("/ai/coach")
def ai_coach(request: CoachRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        result = chat_with_coach(
            messages=request.messages,
            user=request.user,
            channel=request.channel,
            profile=request.profile,
            taskContext=request.taskContext,
            niche=request.niche,
            lang=request.lang
        )
        return {"reply": result["answer"], "sources": result.get("sources", [])}
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Goal Roadmap Endpoint
# -------------------------
@app.post("/ai/goal-roadmap")
def goal_roadmap(request: GoalRoadmapRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return estimate_goal_timeline(request.dict())
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Task Guide Endpoint
# -------------------------
@app.post("/ai/task-guide")
def task_guide(request: TaskGuideRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return generate_task_guide(request.dict())
    except Exception as e:
        return {"error": str(e)}