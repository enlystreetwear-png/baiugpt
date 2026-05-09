# core/model.py

from typing import Dict, Any, List, Optional
from research.research import research_answer  # RAG + web search + reasoning
import textwrap

# -------------------------
# Weekly Plan
# -------------------------
def generate_weekly_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    profile = payload.get("profile", {})
    snapshots = payload.get("snapshots", [])
    niche = profile.get("nicheDesc") or profile.get("niche") or "content creation"
    lang = profile.get("lang") or "English"

    tasks = [
        {
            "id": "idea-1",
            "type": "video",
            "title": f"Create one high-retention {niche} video",
            "detail": f"Plan the hook, main payoff, and call to action in {lang}.",
            "time": "2-3 hours",
            "priority": "high",
            "isIdea": True,
        },
        {
            "id": "short-1",
            "type": "short",
            "title": "Cut 3 Shorts from your strongest moment",
            "detail": "Use one clear moment per Short and add readable captions.",
            "time": "60 min",
            "priority": "high",
            "isIdea": True,
        },
        {
            "id": "thumb-1",
            "type": "seo",
            "title": "Rewrite titles and thumbnails for clarity",
            "detail": "Use one promise, one emotion, and one visual focus.",
            "time": "45 min",
            "priority": "medium",
        },
        {
            "id": "engage-1",
            "type": "engage",
            "title": "Reply to comments and pin a question",
            "detail": "Ask viewers what they want next so the next video is easier to choose.",
            "time": "20 min",
            "priority": "medium",
        },
    ]

    return {
        "summary": f"Weekly plan for '{channel.get('title') or channel.get('name') or 'Your Channel'}' using {len(snapshots)} snapshots.",
        "focus": f"Grow the {niche} channel with stronger hooks, repeatable formats, and Shorts.",
        "tasks": tasks,
    }

# -------------------------
# Analysis
# -------------------------
def generate_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    snapshots = payload.get("snapshots", [])
    return {
        "summary": f"Analyzed '{channel.get('title') or channel.get('name') or 'Your Channel'}' using {len(snapshots)} snapshots.",
        "insights": [
            {"emoji": "[Focus]", "text": "Focus each video on one viewer promise so titles, thumbnails, and hooks match."},
            {"emoji": "[Hook]", "text": "Move the payoff into the first 10 seconds to improve retention."},
            {"emoji": "[Growth]", "text": "Turn your best long-video moments into Shorts to create more discovery paths."},
        ],
        "bestDay": "Saturday",
    }

# -------------------------
# Analyze Channel
# -------------------------
def analyze_channel(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    videos = payload.get("videos", [])
    return {
        "channel_analysis": f"Analyzed {len(videos)} videos for channel '{channel.get('title') or channel.get('name') or 'Your Channel'}'.",
        "strengths": ["Clear niche direction", "Room to build repeatable series"],
        "opportunities": ["Sharper hooks", "More Shorts from existing videos", "Cleaner thumbnail promise"],
    }

# -------------------------
# AI Coach (internet + reasoning)
# -------------------------
def chat_with_coach(
    messages=None,
    user=None,
    channel=None,
    profile=None,
    taskContext=None,
    niche=None,
    lang=None,
):
    prompt_parts = []

    user_texts = []

    if messages:
        for message in messages:
            text = message.get("text") or message.get("content") or message.get("message")
            if text:
                user_texts.append(text)
                prompt_parts.append(text)

    if channel:
        prompt_parts.append(f"Channel context: {channel}")
    if profile:
        prompt_parts.append(f"Creator profile: {profile}")
    if taskContext:
        prompt_parts.append(f"Current task: {taskContext}")

    prompt = "\n".join(prompt_parts) if prompt_parts else "Give YouTube creator growth advice"
    if niche:
        prompt += f"\nNiche: {niche}"
    if lang:
        prompt += f"\nLanguage: {lang}"

    research_question = " ".join(user_texts) if user_texts else prompt
    result = research_answer(research_question, niche=niche)
    # Expect result to have "answer" and "sources"
    answer_text = result.get("answer", "I could not find an answer.")
    sources = result.get("sources", [])
    return {"answer": answer_text, "sources": sources}

# -------------------------
# Goal Roadmap
# -------------------------
def estimate_goal_timeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    snapshots = payload.get("snapshots", [])
    return {
        "timeline": f"Goal roadmap for '{channel.get('title') or channel.get('name') or 'Your Channel'}' with {len(snapshots)} snapshots.",
        "roadmap": [
            {"label": "This week", "action": "Publish one focused video and three Shorts."},
            {"label": "Next 30 days", "action": "Repeat the best performing format four times."},
            {"label": "Next 90 days", "action": "Double down on topics with the highest retention and comments."},
        ],
    }

# -------------------------
# Task Guide
# -------------------------
def generate_task_guide(payload: Dict[str, Any]) -> Dict[str, Any]:
    task = payload.get("task", {})
    channel = payload.get("channel", {})
    title = task.get("title") or task.get("name") or "TubeCoach task"
    niche = task.get("niche") or payload.get("profile", {}).get("niche") or "content creation"
    lang = task.get("lang") or payload.get("profile", {}).get("lang") or "English"

    return {
        "totalTime": "3-4 hours",
        "steps": [
            {
                "stepNum": 1,
                "title": "Define the viewer promise",
                "timestamp": "Planning",
                "duration": "20 min",
                "what": f"Write one sentence explaining why a {niche} viewer should care about '{title}'.",
                "script": f"Today I will show you the simplest way to get this result in {lang}.",
                "onScreen": "Show the final result or strongest example first.",
                "tip": "One clear promise beats five weak ideas.",
            },
            {
                "stepNum": 2,
                "title": "Build the hook",
                "timestamp": "0:00 - 0:15",
                "duration": "30 min",
                "what": "Open with the payoff, mistake, challenge, or before-after result.",
                "script": f"If you are stuck with this, watch this before you make your next {niche} video.",
                "onScreen": "Show a fast preview of the most interesting moment.",
                "tip": "Avoid long intros and ask for attention only after earning it.",
            },
            {
                "stepNum": 3,
                "title": "Record the main content",
                "timestamp": "0:15 - 3:00",
                "duration": "90 min",
                "what": "Explain the task in simple steps and remove anything that does not support the promise.",
                "script": f"Step one is this. Step two is this. Here is the mistake most creators make.",
                "onScreen": "Show each step with captions or clear examples.",
                "tip": "Keep cuts tight and reset attention every 20 to 30 seconds.",
            },
            {
                "stepNum": 4,
                "title": "Package for upload",
                "timestamp": "Upload",
                "duration": "45 min",
                "what": "Create a title and thumbnail that say the same promise in different ways.",
                "script": "Use the title for the promise and the thumbnail for the emotion or result.",
                "onScreen": "Compare two thumbnail options at small size.",
                "tip": "If it is not readable on mobile, simplify it.",
            },
        ],
        "seoContent": {
            "title": {
                "option1": f"{title} - Simple {niche} Growth Plan",
                "option2": f"How To Improve Your Next {niche} Video",
                "option3": f"{niche.title()} Creator Tips",
            },
            "description": f"Use this {lang} creator plan to improve your next YouTube video with a stronger hook, clearer structure, and better packaging.",
            "tags": ["youtube growth", niche, "creator tips", "video strategy", "TubeCoach", "BaiuGPT"],
            "thumbnailConcept": "One clear result, one short phrase, high contrast, and no clutter.",
            "firstComment": "What topic should I cover next?",
        },
    }
