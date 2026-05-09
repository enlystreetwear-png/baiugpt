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
            "best sensitivity and HUD settings for beginners",
            "new season update explained in simple Tamil",
            "top 5 mistakes that make players lose fights",
            "budget gaming phone settings for smooth FPS",
            "one-life challenge gameplay with clutch moments",
        ]
    elif "cook" in lower or "food" in lower or "recipe" in lower:
        topics = [
            "5-minute rava upma breakfast",
            "high-protein paneer lunch box",
            "one-pot tomato rice dinner",
            "street-style chilli idli at home",
            "no-oven biscuit pudding",
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


def _is_cooking_niche(niche: str) -> bool:
    return any(term in niche.lower() for term in ("cook", "food", "recipe"))


def _is_gaming_niche(niche: str) -> bool:
    return any(term in niche.lower() for term in ("game", "gaming", "gamer", "esports"))


def _is_tamil(lang: str) -> bool:
    return "tamil" in lang.lower()


def _cooking_script_lines(trend: str, lang: str) -> Dict[str, str]:
    if _is_tamil(lang):
        return {
            "hook": f"இன்று {trend} ரெசிபியை ரொம்ப சுலபமா, வீட்டில் இருக்கிற பொருட்களோட செய்து காட்ட போறேன்.",
            "ingredients": "தேவையான பொருட்கள் எல்லாம் screen-ல இருக்கு. அளவுகளை சரியா follow பண்ணுங்க, taste perfect ஆகும்.",
            "cook": "இப்போ flame medium-ல வைத்து, இந்த texture வரும் வரை mix பண்ணணும். இதுதான் taste-க்கு முக்கியமான step.",
            "finish": "இந்த மாதிரி soft/crispy texture வந்ததும் ready. Try பண்ணிட்டு comment-ல எப்படி வந்துச்சுனு சொல்லுங்க.",
        }

    return {
        "hook": f"Today I am making {trend} with simple ingredients and a shortcut that keeps the taste strong.",
        "ingredients": "Here are all the ingredients. Keep the measurements close so the texture comes out right.",
        "cook": "Cook on medium heat until you see this texture. This is the step that builds the flavor.",
        "finish": "Once it looks like this, plate it hot. Try it and comment what recipe I should make next.",
    }


def _content_pack(niche: str, trend: str, secondary: str, lang: str) -> Dict[str, Any]:
    if _is_cooking_niche(niche):
        scripts = _cooking_script_lines(trend, lang)
        title_topic = trend.replace(" recipe", "").strip()
        return {
            "content_type": "recipe",
            "titles": {
                "option1": f"{title_topic.title()} | Easy Tamil Home Recipe" if _is_tamil(lang) else f"{title_topic.title()} | Easy Home Recipe",
                "option2": f"{title_topic.title()} in 10 Minutes | No Complicated Steps",
                "option3": f"Quick {title_topic.title()} for Busy Days",
            },
            "description": (
                f"Learn how to make {trend} with simple ingredients, clear measurements, texture checkpoints, "
                f"and beginner-friendly cooking tips. This video is designed for quick home cooking and easy repeat practice."
            ),
            "tags": [
                "easy recipe",
                "quick recipe",
                "home cooking",
                "Tamil recipe" if _is_tamil(lang) else "cooking",
                trend,
                secondary,
                "breakfast recipe",
                "lunch box recipe",
                "simple ingredients",
                "TubeCoach",
                "BaiuGPT",
            ],
            "thumbnail": f"Close-up finished dish, spoon lift or break shot, steam/texture visible, text: {trend.split()[0].upper()} READY.",
            "first_comment": f"Should I make {secondary} next? Comment YES or tell me your favorite dish.",
            "scripts": scripts,
        }

    if _is_gaming_niche(niche):
        return {
            "content_type": "gaming",
            "titles": {
                "option1": f"{trend.title()} | Tamil Gaming Guide",
                "option2": f"I Tried {trend.title()} So You Can Win More",
                "option3": f"{trend.title()} - Stop Making This Mistake",
            },
            "description": (
                f"In this {lang} gaming video, learn {trend} with practical gameplay examples, "
                f"mistake breakdowns, and a simple setup you can copy before your next match."
            ),
            "tags": [
                "gaming",
                "Tamil gaming" if _is_tamil(lang) else "gaming guide",
                trend,
                secondary,
                "gameplay tips",
                "best settings",
                "beginner guide",
                "pro tips",
                "TubeCoach",
                "BaiuGPT",
            ],
            "thumbnail": f"Gameplay action screenshot, big arrow/circle on the key setting or mistake, text: WIN MORE.",
            "first_comment": f"Want a full guide on {secondary}? Comment NEXT.",
            "scripts": {
                "hook": (
                    f"இந்த setting/mistake சரி பண்ணினா உங்கள் gameplay உடனே improve ஆகும்."
                    if _is_tamil(lang) else
                    "Fix this one setting or mistake and your gameplay will feel better immediately."
                ),
                "setup": "First copy these settings, then test them in one match before changing anything else.",
                "proof": "Here is the exact moment where this helps: aim stays stable, movement is cleaner, and fights are easier to control.",
                "finish": "Try this in your next match and comment your result. I will make the next guide from your comments.",
            },
        }

    return {
        "content_type": "review",
        "titles": {
            "option1": f"{trend}: Worth It or Overhyped?",
            "option2": f"Before You Choose {trend}, Watch This",
            "option3": f"{trend} vs {secondary}: Honest Verdict",
        },
        "description": (
            f"In this {lang} {niche} video, we look at {trend}, compare it with {secondary}, "
            "and decide who should use it, buy it, or skip it."
        ),
        "tags": ["youtube growth", niche, trend, secondary, "review", "comparison", "buyer guide", "TubeCoach", "BaiuGPT"],
        "thumbnail": f"Show {trend} with a big verdict word like WORTH IT? or SKIP? and one clean product/result image.",
        "first_comment": f"Should I test {secondary} next? Comment your choice.",
        "scripts": {
            "hook": f"Before you buy, try, or skip this, here are the 3 things that matter most in {lang}.",
            "ingredients": "Point one is value. Point two is real-world use. Point three is who should avoid it.",
            "cook": "Here is the real-world test result and what it means for you.",
            "finish": "My final verdict is simple: choose it only if these points match your need.",
        },
    }


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
        or "gaming" in lower_niche
        or "game" in lower_niche
        or "gamer" in lower_niche
        or "esports" in lower_niche
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
    pack = _content_pack(niche, primary, secondary, lang)
    is_recipe = pack["content_type"] == "recipe"
    is_gaming = pack["content_type"] == "gaming"

    tasks = [
        {
            "id": "idea-1",
            "type": "video",
            "title": f"Create: {primary}",
            "detail": (
                f"Record a complete recipe video with final dish first, ingredients, cooking checkpoints, and plating."
                if is_recipe else
                f"Record gameplay proof, show the exact setting/mistake, then explain how viewers can copy it."
                if is_gaming else
                f"Use the trend angle '{primary}' and open with the viewer payoff in {lang}."
            ),
            "time": "2-3 hours",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[0].get("snippet") or f"This topic appeared in current {niche} trend research.",
        },
        {
            "id": "short-1",
            "type": "short",
            "title": f"Short: {secondary}",
            "detail": (
                "Make a 30-45 second Short showing the final dish, 3 fast steps, and one taste/texture close-up."
                if is_recipe else
                "Make a 30-45 second Short with one clutch moment, one setting tip, and one result caption."
                if is_gaming else
                "Give one clear yes/no verdict, one proof point, and one comment question."
            ),
            "time": "60 min",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[1].get("snippet") if len(trends) > 1 else "",
        },
        {
            "id": "thumb-1",
            "type": "seo",
            "title": f"Package: {third}",
            "detail": (
                "Create 3 title options, a food close-up thumbnail, description, tags, and pinned comment."
                if is_recipe else
                "Create a gameplay thumbnail, 3 searchable titles, tags, and a pinned question for the next guide."
                if is_gaming else
                "Write 3 titles: best-for-budget, mistake-to-avoid, and honest-verdict."
            ),
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
    is_cooking = _is_cooking_niche(niche)
    pack = _content_pack(niche, trend, secondary, lang)

    if is_cooking:
        return {
            "totalTime": "2-3 hours",
            "steps": [
                {
                    "stepNum": 1,
                    "title": "Plan the recipe promise",
                    "timestamp": "Planning",
                    "duration": "20 min",
                    "what": f"Turn '{trend}' into one clear promise: quick, budget, healthy, kid-friendly, or hotel-style.",
                    "script": pack["scripts"]["hook"],
                    "onScreen": "Show the finished dish first, then show all ingredients in one clean shot.",
                    "tip": "Start with the final dish. Viewers decide to watch with their eyes first.",
                },
                {
                    "stepNum": 2,
                    "title": "Shoot ingredients and prep",
                    "timestamp": "0:00 - 0:20",
                    "duration": "25 min",
                    "what": "Show exact ingredients, quantities, substitutions, and one prep shortcut.",
                    "script": pack["scripts"]["ingredients"],
                    "onScreen": "Ingredient flat-lay, measurement captions, chopping/prep close-ups.",
                    "tip": "Keep measurements on screen long enough to pause and read.",
                },
                {
                    "stepNum": 3,
                    "title": "Film texture checkpoints",
                    "timestamp": "0:20 - 2:30",
                    "duration": "75 min",
                    "what": "Show flame level, timing, color change, texture, and the mistake to avoid.",
                    "script": pack["scripts"]["cook"],
                    "onScreen": "Close-ups of pan/pot texture, timer overlay, flame level caption.",
                    "tip": "Texture checkpoints make the recipe feel trustworthy and easy to repeat.",
                },
                {
                    "stepNum": 4,
                    "title": "Plate, taste, and create Shorts",
                    "timestamp": "Upload",
                    "duration": "40 min",
                    "what": "Record final plating, taste reaction, and two Shorts: final reveal plus one mistake/tip.",
                    "script": pack["scripts"]["finish"],
                    "onScreen": "Final plate close-up, spoon pull/break shot, text overlay with recipe name.",
                    "tip": "Use sensory words like crispy, creamy, spicy, soft, quick, and budget.",
                },
            ],
            "seoContent": {
                "title": pack["titles"],
                "description": pack["description"],
                "tags": pack["tags"],
                "thumbnailConcept": pack["thumbnail"],
                "firstComment": pack["first_comment"],
            },
            "trends": trends,
            "sources": _trend_sources(trends),
        }

    if _is_gaming_niche(niche):
        return {
            "totalTime": "2-3 hours",
            "steps": [
                {
                    "stepNum": 1,
                    "title": "Pick the gameplay proof",
                    "timestamp": "Planning",
                    "duration": "20 min",
                    "what": f"Choose one real match moment that proves '{trend}' helps the viewer play better.",
                    "script": pack["scripts"]["hook"],
                    "onScreen": "Show the best clutch, before-after aim/movement, or settings screen in the first 3 seconds.",
                    "tip": "Gaming viewers need proof fast. Show the result before explaining.",
                },
                {
                    "stepNum": 2,
                    "title": "Show exact settings or mistake",
                    "timestamp": "0:00 - 0:30",
                    "duration": "35 min",
                    "what": "Display the setting, control, loadout, or mistake clearly so viewers can copy it.",
                    "script": pack["scripts"]["setup"],
                    "onScreen": "Use zoom, arrows, and captions for sensitivity, HUD, graphics, or movement details.",
                    "tip": "Make every number and setting readable on mobile.",
                },
                {
                    "stepNum": 3,
                    "title": "Break down one fight",
                    "timestamp": "0:30 - 2:30",
                    "duration": "70 min",
                    "what": f"Use one gameplay fight to show why '{trend}' works and where players usually fail.",
                    "script": pack["scripts"]["proof"],
                    "onScreen": "Pause at the key moment, circle the enemy/player movement, then replay it at normal speed.",
                    "tip": "One clear fight breakdown is stronger than five random clips.",
                },
                {
                    "stepNum": 4,
                    "title": "Package as guide plus Short",
                    "timestamp": "Upload",
                    "duration": "40 min",
                    "what": "Upload the full guide and cut the strongest 20-second proof moment as a Short.",
                    "script": pack["scripts"]["finish"],
                    "onScreen": "Thumbnail should show gameplay action, a marked setting/mistake, and 2-3 words.",
                    "tip": "Use comments to choose the next settings/loadout/challenge video.",
                },
            ],
            "seoContent": {
                "title": pack["titles"],
                "description": pack["description"],
                "tags": pack["tags"],
                "thumbnailConcept": pack["thumbnail"],
                "firstComment": pack["first_comment"],
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
            "title": pack["titles"],
            "description": pack["description"],
            "tags": pack["tags"],
            "thumbnailConcept": pack["thumbnail"],
            "firstComment": pack["first_comment"],
        },
        "trends": trends,
        "sources": _trend_sources(trends),
    }
