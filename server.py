# server.py

from fastapi import FastAPI, Header, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from native.memory import remember_feedback
from native.reasoner import (
    native_answer,
    native_status,
    refine_task_guide,
    refine_weekly_plan,
)

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

class NativeGenerateRequest(BaseModel):
    prompt: str
    niche: Optional[str] = "content creation"
    lang: Optional[str] = "English"

class NativeFeedbackRequest(BaseModel):
    niche: Optional[str] = ""
    lang: Optional[str] = ""
    rating: Optional[int] = None
    question: Optional[str] = ""
    badOutput: Optional[Any] = None
    betterOutput: Optional[Any] = None
    notes: Optional[str] = ""

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

@app.get("/native/status")
def native_status_route(x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    return native_status()

# -------------------------
# Weekly Plan Endpoint
# -------------------------
@app.post("/ai/weekly-plan")
def weekly_plan(request: WeeklyPlanRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        payload = request.dict()
        return refine_weekly_plan(payload, generate_weekly_plan(payload))
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

@app.post("/ai/native-generate")
def native_generate(request: NativeGenerateRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return native_answer(request.prompt, niche=request.niche or "content creation", lang=request.lang or "English")
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/native-feedback")
def native_feedback(request: NativeFeedbackRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return remember_feedback(request.dict())
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
        payload = request.dict()
        return refine_task_guide(payload, generate_task_guide(payload))
    except Exception as e:
        return {"error": str(e)}
