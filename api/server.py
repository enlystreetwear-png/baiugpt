from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from core.ai_project import (
    generate_weekly_plan,    # your BaiuGPT project functions
    generate_analysis,
    analyze_channel,
    chat_with_coach,
    estimate_goal_timeline,
    generate_task_guide
)

API_KEY = "baiu-secret-12345"

app = FastAPI(title="BaiuGPT AI API")


# =======================
# REQUEST SCHEMAS
# =======================
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


# =======================
# AUTH CHECK
# =======================
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# =======================
# ENDPOINTS
# =======================
@app.post("/ai/weekly-plan")
async def weekly_plan(request: WeeklyPlanRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return generate_weekly_plan(request.channel, request.profile, request.snapshots)


@app.post("/ai/analysis")
async def analysis(request: AnalysisRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return generate_analysis(request.channel, request.profile, request.snapshots)


@app.post("/ai/analyze-channel")
async def analyze_channel_endpoint(request: AnalyzeChannelRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return analyze_channel(request.channel, request.videos)


@app.post("/ai/coach")
async def coach(request: CoachRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return chat_with_coach(request)


@app.post("/ai/goal-roadmap")
async def goal_roadmap(request: GoalRoadmapRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return estimate_goal_timeline(request.channel, request.profile, request.snapshots)


@app.post("/ai/task-guide")
async def task_guide(request: TaskGuideRequest, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return generate_task_guide(request.task, request.channel, request.profile)