# server.py

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from native.code_agent import code_agent_answer
from native.memory import remember_feedback
from native.online_learning import learn_online
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
    niche: Optional[str] = "Tech Reviews"
    lang: Optional[str] = "English"
    messages: Optional[List[Dict[str, Any]]] = []

class NativeFeedbackRequest(BaseModel):
    niche: Optional[str] = ""
    lang: Optional[str] = ""
    rating: Optional[int] = None
    question: Optional[str] = ""
    badOutput: Optional[Any] = None
    betterOutput: Optional[Any] = None
    notes: Optional[str] = ""

class NativeOnlineLearnRequest(BaseModel):
    query: str
    niche: Optional[str] = "content creation"
    lang: Optional[str] = "English"
    maxResults: Optional[int] = 5

class CodeAgentRequest(BaseModel):
    prompt: str

# -------------------------
# FastAPI Setup
# -------------------------
app = FastAPI(title="BaiuGPT API", version="0.1.0")
UI_DIR = Path(__file__).resolve().parent / "ui"

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "name": "BaiuGPT"}

@app.get("/")
def root():
    return RedirectResponse(url="/chat")

@app.get("/chat")
def chat_page():
    index_path = UI_DIR / "chat.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Chat UI not found")
    return FileResponse(str(index_path))

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
        user_text = " ".join(
            str(message.get("text") or message.get("content") or message.get("message") or "")
            for message in (request.messages or [])
        ).strip()
        online_learning = None
        if user_text:
            online_learning = learn_online(
                user_text,
                niche=request.niche or (request.profile or {}).get("niche") or "content creation",
                lang=request.lang or (request.profile or {}).get("lang") or "English",
                max_results=3,
                deep=True,
            )
        result = chat_with_coach(
            messages=request.messages,
            user=request.user,
            channel=request.channel,
            profile=request.profile,
            taskContext=request.taskContext,
            niche=request.niche,
            lang=request.lang
        )
        sources = result.get("sources", [])
        if online_learning:
            sources = online_learning.get("sources", []) + sources
        return {"reply": result["answer"], "sources": sources, "nativeLearning": online_learning}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/native-generate")
def native_generate(request: NativeGenerateRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        niche = request.niche or "Tech Reviews"
        lang = request.lang or "English"
        messages = request.messages or [{"role": "user", "text": request.prompt}]
        result = chat_with_coach(
            messages=messages,
            user={},
            channel={},
            profile={"niche": niche, "lang": lang},
            taskContext=None,
            niche=niche,
            lang=lang,
        )
        return {"answer": result.get("answer", ""), "sources": result.get("sources", []), "mode": "tubecoach"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/native-feedback")
def native_feedback(request: NativeFeedbackRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return remember_feedback(request.dict())
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/native-online-learn")
def native_online_learn(request: NativeOnlineLearnRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return learn_online(
            request.query,
            niche=request.niche or "content creation",
            lang=request.lang or "English",
            max_results=request.maxResults or 5,
            deep=True,
        )
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/code-agent")
def code_agent(request: CodeAgentRequest, x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
    try:
        return code_agent_answer(request.prompt)
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
