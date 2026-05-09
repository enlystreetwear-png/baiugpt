# core/model.py

from typing import Dict, Any, List, Optional
from research.research import research_answer, search_web
import re


def _clean_text(value: Any, fallback: str = "") -> str:
    text = str(value or fallback).strip()
    return re.sub(r"\s+", " ", text)


def _channel_name(channel: Dict[str, Any]) -> str:
    return _clean_text(channel.get("title") or channel.get("name"), "Your Channel")


def _profile_niche(profile: Dict[str, Any], fallback: str = "content creation") -> str:
    return _clean_text(profile.get("nicheDesc") or profile.get("niche"), fallback)


def _profile_lang(profile: Dict[str, Any], fallback: str = "English") -> str:
    return _clean_text(profile.get("lang"), fallback)


def _fallback_trends(niche: str) -> List[Dict[str, str]]:
    lower = niche.lower()
    if "tech" in lower or "review" in lower:
        topics = [
            "AI smartphone features: useful or gimmick",
            "Best budget phone camera test",
            "Laptop buying guide: Intel vs AMD vs Snapdragon",
            "Best earbuds for calls, gaming, and battery life",
            "Creator desk gadgets under a budget",
        ]
    elif "gaming" in lower:
        topics = [
            "Best settings for smoother gameplay",
            "New update explained simply",
            "Beginner mistakes to avoid",
            "Budget gaming setup tips",
            "Challenge run with a clear rule",
        ]
    elif "cook" in lower or "food" in lower or "recipe" in lower:
        topics = [
            "5-minute breakfast recipe for busy mornings",
            "High-protein lunch box under budget",
            "One-pot dinner with simple ingredients",
            "Street-style recipe made healthier at home",
            "No-oven dessert with 3 ingredients",
        ]
    else:
        topics = [
            f"{niche} beginner mistakes",
            f"{niche} tools worth trying",
            f"{niche} trend explained",
            f"{niche} before and after improvement",
            f"{niche} weekly challenge",
        ]

    return [
        {
            "topic": topic,
            "name": topic,
            "title": topic,
            "url": "",
            "snippet": f"Actionable {niche} video idea selected for this week's creator plan.",
            "score": 95 - (index * 7),
        }
        for index, topic in enumerate(topics)
    ]


def _short_topic(title: str, niche: str) -> str:
    title = re.sub(r"\s*[-–|:]\s*(YouTube|Google|Forbes|Reddit|Guide|Review|AIR Media-Tech|Beacons).*$", "", title, flags=re.I)
    title = re.sub(r"\b(2024|2025|2026)\b", "", title)
    title = re.sub(r"\s+", " ", title).strip(" -:|")
    if len(title) > 72:
        title = title[:72].rsplit(" ", 1)[0]
    return title or f"{niche} trend"


def _trend_context(niche: str, intent: str = "") -> List[Dict[str, str]]:
    lower_niche = niche.lower()
    if (
        "tech" in lower_niche
        or "review" in lower_niche
        or "cook" in lower_niche
        or "food" in lower_niche
        or "recipe" in lower_niche
    ):
        return _fallback_trends(niche)

    query = (
        f"{niche} latest product trends buyer questions comparison topics "
        f"new launches problems worth it review ideas {intent}"
    )
    try:
        results = search_web(query, max_results=8)
    except Exception:
        results = []

    trends = []
    blocked = (
        "dictionary",
        "definition",
        "windows account",
        "login",
        "username",
        "top tech youtubers",
        "tech review youtubers",
        "tech youtube channels",
        "popular tech reviewers",
        "influencer list",
        "news sites",
        "sites to follow",
        "techradar",
        "shopify",
        "examples and trends",
        "youtube channels to watch",
    )
    for result in results:
        title = _clean_text(result.get("title"))
        url = _clean_text(result.get("url"))
        snippet = _clean_text(result.get("snippet"))
        blob = f"{title} {url} {snippet}".lower()
        if not title or any(term in blob for term in blocked):
            continue
        trends.append({
            "topic": _short_topic(title, niche),
            "name": _short_topic(title, niche),
            "title": title,
            "url": url,
            "snippet": snippet,
            "score": 95 - (len(trends) * 7),
        })
        if len(trends) >= 5:
            break

    if len(trends) < 3:
        return _fallback_trends(niche)

    return trends


def _trend_sources(trends: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": item.get("title", item.get("topic", "")), "url": item.get("url", "")}
        for item in trends
        if item.get("url")
    ]

# -------------------------
# Weekly Plan
# -------------------------
def generate_weekly_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    profile = payload.get("profile", {})
    snapshots = payload.get("snapshots", [])
    niche = _profile_niche(profile)
    lang = _profile_lang(profile)
    trends = _trend_context(niche, "weekly action plan")
    primary = trends[0]["topic"]
    secondary = trends[1]["topic"] if len(trends) > 1 else f"{niche} comparison"
    third = trends[2]["topic"] if len(trends) > 2 else f"{niche} buyer guide"

    tasks = [
        {
            "id": "idea-1",
            "type": "video",
            "title": f"Make a trend-backed video: {primary}",
            "detail": f"Use the trend angle '{primary}' and open with the viewer payoff in {lang}.",
            "time": "2-3 hours",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[0].get("snippet") or f"This topic appeared in current {niche} trend research.",
        },
        {
            "id": "short-1",
            "type": "short",
            "title": f"Post a 45-second verdict Short: {secondary}",
            "detail": "Give one clear yes/no verdict, one proof point, and one comment question.",
            "time": "60 min",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[1].get("snippet") if len(trends) > 1 else "",
        },
        {
            "id": "thumb-1",
            "type": "seo",
            "title": f"Package a buyer-guide angle: {third}",
            "detail": "Write 3 titles: best-for-budget, mistake-to-avoid, and honest-verdict.",
            "time": "45 min",
            "priority": "medium",
            "trendReason": trends[2].get("snippet") if len(trends) > 2 else "",
        },
        {
            "id": "engage-1",
            "type": "engage",
            "title": f"Ask viewers which {niche} topic to test next",
            "detail": f"Pin a comment with two options: '{primary}' or '{secondary}'.",
            "time": "20 min",
            "priority": "medium",
        },
    ]

    return {
        "summary": f"Weekly plan for '{_channel_name(channel)}' using {len(snapshots)} snapshots and current {niche} trend signals.",
        "focus": f"Win this week with trend-led {niche} topics, stronger hooks, and mobile-first packaging.",
        "tasks": tasks,
        "trends": trends,
        "sources": _trend_sources(trends),
    }

# -------------------------
# Analysis
# -------------------------
def generate_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    profile = payload.get("profile", {})
    snapshots = payload.get("snapshots", [])
    niche = _profile_niche(profile)
    trends = _trend_context(niche, "analytics insight")
    top_topic = trends[0]["topic"]
    return {
        "summary": f"Analyzed '{_channel_name(channel)}' using {len(snapshots)} snapshots and current {niche} topic signals.",
        "insights": [
            {"emoji": "[Trend]", "text": f"Make the next video around '{top_topic}' because it matches current {niche} search/trend signals."},
            {"emoji": "[Hook]", "text": "Start with the final verdict or result in the first 10 seconds, then explain the proof."},
            {"emoji": "[Package]", "text": "Use a title/thumbnail pair that promises one outcome: save money, avoid a mistake, or choose faster."},
        ],
        "bestDay": "Saturday",
        "trends": trends,
        "sources": _trend_sources(trends),
    }

# -------------------------
# Analyze Channel
# -------------------------
def analyze_channel(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    videos = payload.get("videos", [])
    titles = [_clean_text(video.get("title")) for video in videos if video.get("title")]
    repeated_terms = []
    for title in titles:
        for word in re.findall(r"[A-Za-z][A-Za-z0-9+.-]{3,}", title.lower()):
            if word not in repeated_terms and sum(word in t.lower() for t in titles) > 1:
                repeated_terms.append(word)
    opportunities = [
        "Turn the strongest topic into a repeatable weekly series.",
        "Make Shorts from the clearest verdict or before-after moment.",
        "Use thumbnails that show the product/result, not just text.",
    ]
    if repeated_terms:
        opportunities.insert(0, f"Double down on recurring viewer interest around: {', '.join(repeated_terms[:3])}.")
    return {
        "channel_analysis": f"Analyzed {len(videos)} videos for channel '{_channel_name(channel)}'.",
        "strengths": ["Clear niche direction", "Existing videos can be repackaged into trend-led Shorts"],
        "opportunities": opportunities,
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
    profile = profile or {}
    niche = niche or _profile_niche(profile)
    lang = lang or _profile_lang(profile)
    trends = _trend_context(niche, prompt)

    if niche:
        prompt += f"\nNiche: {niche}"
    if lang:
        prompt += f"\nLanguage: {lang}"

    research_question = " ".join(user_texts) if user_texts else prompt
    task_title = ""
    if isinstance(taskContext, dict):
        task_title = taskContext.get("title") or taskContext.get("name") or ""

    if research_question.strip().lower() in {"hi", "hello", "hey", "hai"}:
        answer_text = (
            f"Hi. For your {niche} channel, the smartest move is to choose one trend angle and turn it into a clear verdict video.\n\n"
            f"Top angle to use now: {trends[0]['topic']}.\n"
            f"Make the hook: 'Before you buy or try this, here is what matters most.'\n"
            f"Then create one Short from the strongest proof point.\n\n"
            f"If you are working on '{task_title or 'this task'}', ask me for a title, hook, script, thumbnail, or SEO pack."
        )
        sources = _trend_sources(trends)
    else:
        result = research_answer(f"{research_question}\nTask: {task_title}\nLanguage: {lang}", niche=niche)
        trend_lines = "\n".join([f"- {item['topic']}" for item in trends[:3]])
        answer_text = (
            f"Smart {niche} recommendation based on current trend signals:\n\n"
            f"{trend_lines}\n\n"
            f"For '{task_title or research_question}', use this structure:\n"
            f"1. Hook: show the final verdict/result first.\n"
            f"2. Proof: compare 2-3 concrete points viewers care about.\n"
            f"3. Decision: say who should use/buy/skip it.\n"
            f"4. Short: cut the strongest 20-45 second verdict as a separate post.\n\n"
            f"{result.get('answer', '').strip()}"
        ).strip()
        sources = _trend_sources(trends) or result.get("sources", [])

    return {"answer": answer_text, "sources": sources}

# -------------------------
# Goal Roadmap
# -------------------------
def estimate_goal_timeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    channel = payload.get("channel", {})
    profile = payload.get("profile", {})
    snapshots = payload.get("snapshots", [])
    niche = _profile_niche(profile)
    trends = _trend_context(niche, "subscriber growth roadmap")
    return {
        "timeline": f"Goal roadmap for '{_channel_name(channel)}' with {len(snapshots)} snapshots and live {niche} topic signals.",
        "roadmap": [
            {"label": "This week", "action": f"Publish one trend-backed video on '{trends[0]['topic']}' and three Shorts from the strongest proof points."},
            {"label": "Next 30 days", "action": f"Build a repeatable series around '{trends[1]['topic'] if len(trends) > 1 else niche}' and compare results weekly."},
            {"label": "Next 90 days", "action": "Double down on topics with the highest click-through rate, retention, and comment demand."},
        ],
        "trends": trends,
        "sources": _trend_sources(trends),
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
    trends = _trend_context(niche, title)
    trend = trends[0]["topic"]
    secondary = trends[1]["topic"] if len(trends) > 1 else f"{niche} comparison"
    is_cooking = any(term in niche.lower() for term in ("cook", "food", "recipe"))

    if is_cooking:
        return {
            "totalTime": "2-3 hours",
            "steps": [
                {
                    "stepNum": 1,
                    "title": "Pick the exact dish promise",
                    "timestamp": "Planning",
                    "duration": "20 min",
                    "what": f"Turn '{trend}' into one clear promise: fast, healthy, budget, beginner-friendly, or restaurant-style.",
                    "script": f"Today I am making {trend} in a simple way, with ingredients you can actually find at home.",
                    "onScreen": "Show the finished dish first, then show all ingredients in one clean shot.",
                    "tip": "Food videos work best when viewers see the final result before the steps.",
                },
                {
                    "stepNum": 2,
                    "title": "Record the hook and ingredients",
                    "timestamp": "0:00 - 0:20",
                    "duration": "25 min",
                    "what": "Start with the plated dish, break it open or taste it, then show the ingredient list.",
                    "script": f"If you want a {niche} idea that is quick and tasty, this one is ready without complicated steps.",
                    "onScreen": "Use quick cuts: final plate, texture close-up, ingredients, first cooking action.",
                    "tip": "Avoid long talking. Let the food visuals sell the video.",
                },
                {
                    "stepNum": 3,
                    "title": "Film each cooking step clearly",
                    "timestamp": "0:20 - 2:30",
                    "duration": "75 min",
                    "what": "Show chopping, mixing, cooking temperature, texture checkpoints, and common mistakes.",
                    "script": "Cook until this texture appears. Do not rush this step, because this is where the taste comes from.",
                    "onScreen": "Add captions for measurements, flame level, timing, and texture changes.",
                    "tip": "For Tamil viewers, keep key measurements visible on screen while explaining naturally.",
                },
                {
                    "stepNum": 4,
                    "title": "Package for Shorts and search",
                    "timestamp": "Upload",
                    "duration": "40 min",
                    "what": "Create one long video and two Shorts: one final reveal, one mistake/tip clip.",
                    "script": "Save this recipe and comment what dish I should make next.",
                    "onScreen": "Thumbnail should show the finished dish, steam/texture, and 2-3 words only.",
                    "tip": "Use sensory words like crispy, creamy, spicy, soft, budget, and quick.",
                },
            ],
            "seoContent": {
                "title": {
                    "option1": f"{trend} | Easy Tamil Recipe",
                    "option2": f"{trend} in Simple Steps",
                    "option3": f"Quick {niche} Recipe Everyone Can Try",
                },
                "description": f"In this {lang} cooking video, learn how to make {trend} with simple ingredients, clear steps, and beginner-friendly tips.",
                "tags": ["cooking", niche, trend, "easy recipe", "Tamil recipe", "home cooking", "quick recipe", "TubeCoach", "BaiuGPT"],
                "thumbnailConcept": f"Close-up of the finished {trend}, one spoon/fork action shot, and text: EASY RECIPE.",
                "firstComment": f"Should I make {secondary} next? Comment your choice.",
            },
            "trends": trends,
            "sources": _trend_sources(trends),
        }

    return {
        "totalTime": "3-4 hours",
        "steps": [
            {
                "stepNum": 1,
                "title": "Choose the trend angle",
                "timestamp": "Planning",
                "duration": "20 min",
                "what": f"Connect '{title}' to the current trend angle '{trend}'.",
                "script": f"Today I am testing whether {trend} is actually worth your attention.",
                "onScreen": "Show the product, result, or comparison table immediately.",
                "tip": "A specific trend angle makes the video feel current and clickable.",
            },
            {
                "stepNum": 2,
                "title": "Build the hook",
                "timestamp": "0:00 - 0:15",
                "duration": "30 min",
                "what": "Open with the verdict, then tease the proof.",
                "script": f"Before you buy, try, or skip this, here are the 3 things that matter most in {lang}.",
                "onScreen": "Show a quick before-after, price/value card, or side-by-side comparison.",
                "tip": "For reviews, viewers stay when they know a decision is coming.",
            },
            {
                "stepNum": 3,
                "title": "Prove the verdict",
                "timestamp": "0:15 - 3:00",
                "duration": "90 min",
                "what": f"Compare '{trend}' against '{secondary}' using 3 viewer-first criteria.",
                "script": "Point one is value. Point two is real-world use. Point three is who should avoid it.",
                "onScreen": "Use score cards, close-ups, and quick captions for each criterion.",
                "tip": "Keep cuts tight and reset attention every 20 to 30 seconds.",
            },
            {
                "stepNum": 4,
                "title": "Package for trend discovery",
                "timestamp": "Upload",
                "duration": "45 min",
                "what": "Create one title for search and one thumbnail for curiosity.",
                "script": "The title should promise the decision. The thumbnail should show the conflict.",
                "onScreen": "Thumbnail: product/result on one side, verdict word on the other.",
                "tip": "Use the trend phrase in the title but keep the thumbnail simple.",
            },
        ],
        "seoContent": {
            "title": {
                "option1": f"{trend}: Worth It or Overhyped?",
                "option2": f"Before You Choose {trend}, Watch This",
                "option3": f"{trend} vs {secondary}: Honest Verdict",
            },
            "description": f"In this {lang} {niche} video, we look at {trend}, compare it with {secondary}, and decide who should use it, buy it, or skip it.",
            "tags": ["youtube growth", niche, trend, secondary, "review", "comparison", "buyer guide", "TubeCoach", "BaiuGPT"],
            "thumbnailConcept": f"Show {trend} with a big verdict word like WORTH IT? or SKIP? and one clean product/result image.",
            "firstComment": f"Should I test {secondary} next? Comment your choice.",
        },
        "trends": trends,
        "sources": _trend_sources(trends),
    }
