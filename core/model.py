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
    kind = _niche_kind(niche)
    if kind == "tech":
        topics = [
            "AI phones vs normal phones: what actually changes",
            "foldable phones durability and repair cost test",
            "budget laptops getting expensive because of AI memory demand",
            "camera-focused phones: zoom, low light, and video test",
            "smart rings and wearables worth buying this year",
        ]
    elif kind == "gaming":
        topics = [
            "BGMI sensitivity settings for stable aim",
            "Free Fire headshot mistakes to avoid",
            "GTA roleplay funny mission challenge",
            "Minecraft survival base in one hour",
            "budget phone graphics settings for smooth FPS",
        ]
    elif kind == "cooking":
        topics = [
            "5-minute rava upma breakfast",
            "high-protein paneer lunch box",
            "one-pot tomato rice dinner",
            "street-style chilli idli at home",
            "no-oven biscuit pudding",
        ]
    elif kind == "fitness":
        topics = [
            "10-minute belly fat home workout",
            "beginner push-up progression",
            "high-protein vegetarian meal prep",
            "morning mobility routine for back pain",
            "fat loss mistakes beginners make",
        ]
    elif kind == "education":
        topics = [
            "3-hour exam revision plan",
            "how to remember formulas faster",
            "common mistakes in board exam answers",
            "study timetable for working students",
            "one chapter explained with examples",
        ]
    elif kind == "beauty":
        topics = [
            "simple daily skincare routine",
            "budget makeup kit for beginners",
            "saree styling mistakes to avoid",
            "frizzy hair routine for humid weather",
            "office look under 10 minutes",
        ]
    elif kind == "finance":
        topics = [
            "monthly budget plan for beginners",
            "SIP investing explained simply",
            "money mistakes in your 20s",
            "how to save your first emergency fund",
            "credit card rules beginners miss",
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
            "snippet": _fallback_reason(niche, topic),
            "score": 95 - (index * 7),
        }
        for index, topic in enumerate(topics)
    ]


def _fallback_reason(niche: str, topic: str) -> str:
    kind = _niche_kind(niche)
    reasons = {
        "tech": f"Review angle: turn '{topic}' into a viewer decision with price, battery, camera/performance, and who should skip it.",
        "gaming": f"Gameplay angle: make '{topic}' useful with one proof clip, exact settings, and a beginner mistake to fix.",
        "cooking": f"Recipe angle: make '{topic}' practical with final dish first, ingredients, texture checkpoints, and one shortcut.",
        "fitness": f"Routine angle: make '{topic}' beginner-safe with form checks, common mistakes, and a 7-day progression.",
        "education": f"Learning angle: teach '{topic}' with one rule, two examples, and one practice question.",
        "beauty": f"Style angle: make '{topic}' visual with before-after proof, affordable steps, and one mistake to avoid.",
        "finance": f"Money angle: explain '{topic}' with simple numbers, one action step, and one mistake to avoid.",
    }
    return reasons.get(kind, f"Creator angle: turn '{topic}' into a clear step-by-step video with proof and a viewer action.")


def _is_cooking_niche(niche: str) -> bool:
    return any(term in niche.lower() for term in ("cook", "food", "recipe"))


def _is_gaming_niche(niche: str) -> bool:
    return any(term in niche.lower() for term in ("game", "gaming", "gamer", "esports"))


def _niche_kind(niche: str) -> str:
    lower = niche.lower()
    if any(term in lower for term in ("cook", "food", "recipe")):
        return "cooking"
    if any(term in lower for term in ("game", "gaming", "gamer", "esports")):
        return "gaming"
    if any(term in lower for term in ("tech", "review", "gadget", "phone", "laptop")):
        return "tech"
    if any(term in lower for term in ("fitness", "workout", "gym", "health", "yoga")):
        return "fitness"
    if any(term in lower for term in ("education", "study", "exam", "learn", "teaching")):
        return "education"
    if any(term in lower for term in ("beauty", "fashion", "makeup", "skincare", "style")):
        return "beauty"
    if any(term in lower for term in ("finance", "money", "invest", "business", "stock")):
        return "finance"
    return "general"


def _is_tamil(lang: str) -> bool:
    return "tamil" in lang.lower()


def _title_case(text: str) -> str:
    small = {"and", "or", "for", "with", "in", "to", "of", "the", "a", "an"}
    words = text.split()
    titled = []
    for index, word in enumerate(words):
        titled.append(word if index > 0 and word.lower() in small else word[:1].upper() + word[1:])
    return " ".join(titled)


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
                "option2": f"{title_topic.title()} Without Complicated Steps",
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
        clean_topic = _title_case(trend)
        return {
            "content_type": "gaming",
            "titles": {
                "option1": f"{clean_topic} - Full Setup + Live Match Test",
                "option2": f"I Changed One Setting and My Aim Felt Better",
                "option3": f"Beginner to Better Aim: Copy This Gameplay Setup",
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

    kind = _niche_kind(niche)
    if kind in {"fitness", "education", "beauty", "finance", "general"}:
        clean_topic = _title_case(trend)
        templates = {
            "fitness": {
                "content_type": "fitness",
                "titles": {
                    "option1": f"{clean_topic} | Beginner-Friendly Routine",
                    "option2": "I Tried This Simple Routine for 7 Days",
                    "option3": "Stop Making These Fitness Mistakes",
                },
                "description": f"This {lang} fitness video explains {trend} with simple steps, common mistakes, and a repeatable routine for beginners.",
                "tags": ["fitness", "home workout", "beginner fitness", trend, secondary, "routine", "health", "TubeCoach", "BaiuGPT"],
                "thumbnail": "Before/after pose or exercise frame, clear body posture, text: START HERE.",
                "first_comment": f"Do you want a full routine for {secondary}? Comment ROUTINE.",
                "scripts": {
                    "hook": "If you are starting fitness, do not begin with a hard routine. Start with this simple method.",
                    "setup": "First check your form. Quality matters more than speed.",
                    "proof": "Here is the mistake most beginners make and how to correct it.",
                    "finish": "Try this for 7 days and comment your result.",
                },
            },
            "education": {
                "content_type": "education",
                "titles": {
                    "option1": f"{clean_topic} Explained Simply",
                    "option2": "Learn This Topic in 10 Minutes",
                    "option3": "Most Students Make This Mistake",
                },
                "description": f"This {lang} education video teaches {trend} with examples, memory tricks, and common exam mistakes.",
                "tags": ["study tips", "education", "exam preparation", trend, secondary, "learning", "student tips", "TubeCoach", "BaiuGPT"],
                "thumbnail": "Notebook or board with one big question, text: EASY METHOD.",
                "first_comment": f"Which chapter should I explain next: {secondary}?",
                "scripts": {
                    "hook": "If this topic feels confusing, I will make it simple in the next few minutes.",
                    "setup": "First understand this one rule. Everything else connects to it.",
                    "proof": "Here is an example and the common mistake students make.",
                    "finish": "Save this and try the practice question in the comments.",
                },
            },
            "beauty": {
                "content_type": "beauty",
                "titles": {
                    "option1": f"{clean_topic} | Simple Beginner Guide",
                    "option2": "Affordable Routine That Actually Looks Good",
                    "option3": "Avoid These Style Mistakes",
                },
                "description": f"This {lang} beauty/fashion video shows {trend} with affordable products, step-by-step application, and mistakes to avoid.",
                "tags": ["beauty", "fashion", "skincare", "makeup", trend, secondary, "beginner guide", "TubeCoach", "BaiuGPT"],
                "thumbnail": "Before/after face or outfit, clean lighting, text: EASY LOOK.",
                "first_comment": f"Should I do {secondary} next? Comment LOOK.",
                "scripts": {
                    "hook": "This is the easiest way to get a clean look without overcomplicating it.",
                    "setup": "Start with this base step because it changes the final result.",
                    "proof": "Here is the before and after so you can see the difference.",
                    "finish": "Save this look and comment what style you want next.",
                },
            },
            "finance": {
                "content_type": "finance",
                "titles": {
                    "option1": f"{clean_topic} - Simple Money Guide",
                    "option2": "Money Mistake You Should Avoid",
                    "option3": "Start Managing Money With This Simple Plan",
                },
                "description": f"This {lang} finance video explains {trend} in simple language with examples, action steps, and mistakes to avoid.",
                "tags": ["personal finance", "money tips", "beginner finance", trend, secondary, "saving money", "investing basics", "TubeCoach", "BaiuGPT"],
                "thumbnail": "Simple money chart or calculator, big number, text: START NOW.",
                "first_comment": f"Want a simple example for {secondary}? Comment MONEY.",
                "scripts": {
                    "hook": "Most beginners lose money because they skip this basic rule.",
                    "setup": "First understand the simple version before you take action.",
                    "proof": "Here is a real example with numbers so it is easy to follow.",
                    "finish": "Save this and comment your next money question.",
                },
            },
            "general": {
                "content_type": "general",
                "titles": {
                    "option1": f"{clean_topic} | Step-by-Step Guide",
                    "option2": "Beginner Mistakes You Should Avoid",
                    "option3": "Simple Method That Actually Works",
                },
                "description": f"This {lang} video explains {trend} with a simple step-by-step process, examples, and clear next actions.",
                "tags": ["how to", "beginner guide", niche, trend, secondary, "tips", "TubeCoach", "BaiuGPT"],
                "thumbnail": "Clear before/after or result image, text: EASY STEPS.",
                "first_comment": f"What should I cover next: {secondary}?",
                "scripts": {
                    "hook": "If you are confused about this, follow these simple steps.",
                    "setup": "Start with the most important step first.",
                    "proof": "Here is an example so you can copy it easily.",
                    "finish": "Try this and comment what you want next.",
                },
            },
        }
        return templates[kind]

    review_scripts = {
        "hook": f"I tested {trend} like a normal buyer, and the answer is not as simple as the hype.",
        "ingredients": "Test one is daily use. Test two is the hidden tradeoff. Test three is whether the price makes sense.",
        "cook": "Here is the real-world test result and what it means for you.",
        "finish": "My final verdict is simple: buy, wait, or skip based on these results.",
    }
    return {
        "content_type": "review",
        "titles": {
            "option1": f"{_title_case(trend)} - Honest Verdict",
            "option2": "I Tested the Feature Viewers Actually Care About",
            "option3": "Before You Upgrade, Check These 3 Things",
        },
        "description": (
            f"In this {lang} {niche} video, we look at {trend}, compare it with {secondary}, "
            "and decide who should use it, buy it, or skip it."
        ),
        "tags": ["youtube growth", niche, trend, secondary, "review", "comparison", "buyer guide", "TubeCoach", "BaiuGPT"],
        "thumbnail": f"Show {trend} with one proof visual: price, camera sample, battery number, repair risk, or speed result.",
        "first_comment": f"Should I test {secondary} next? Comment your choice.",
        "scripts": review_scripts,
    }


def _pack_titles(pack: Dict[str, Any]) -> List[str]:
    titles = pack.get("titles", [])
    if isinstance(titles, dict):
        return [str(value) for value in titles.values() if value]
    if isinstance(titles, list):
        return [str(value) for value in titles if value]
    return []


def _short_topic(title: str, niche: str) -> str:
    title = re.sub(r"\s*[-–|:]\s*(YouTube|Google|Forbes|Reddit|Guide|Review|AIR Media-Tech|Beacons|Tom's Guide|TechRadar|Android Central|Android Authority|PhoneArena).*$", "", title, flags=re.I)
    title = re.sub(r"\b(2024|2025|2026)\b", "", title)
    title = re.sub(r"\b(best|top)\s+\d+\s+", "", title, flags=re.I)
    title = re.sub(r"\b(the\s+)?best\s+", "", title, flags=re.I)
    title = re.sub(r"\s+", " ", title).strip(" -:|")
    if len(title) > 72:
        title = title[:72].rsplit(" ", 1)[0]
    return title or f"{niche} trend"


def _tech_review_topic(title: str, snippet: str) -> str:
    blob = f"{title} {snippet}".lower()
    if "smartphone trends" in blob:
        return "smartphone trends to test: AI, battery, foldables, and price"
    if "phones we've tested" in blob or "best phones" in blob or "top smartphones" in blob:
        return "smartphone buyer guide: best value, camera, battery, and updates"
    if ("buyer" in blob or "buying" in blob) and ("smartphone" in blob or "mobile phone" in blob or "phone" in blob):
        return "smartphone buyer guide: best value, camera, battery, and updates"
    if "ramageddon" in blob or "memory" in blob and ("laptop" in blob or "phone" in blob):
        return "AI memory shortage: should viewers buy phones and laptops now"
    if "fold" in blob or "foldable" in blob:
        return "foldable phones durability, repair cost, and buyer risk"
    if "ai phone" in blob or "ai phones" in blob or "ai features" in blob:
        return "AI phone features: useful tools or marketing gimmick"
    if "camera" in blob or "photography" in blob or "zoom" in blob:
        return "camera phone test: zoom, low light, and video quality"
    if "laptop" in blob or "macbook" in blob or "chromebook" in blob:
        return "laptop buying guide: performance, battery, and upgrade timing"
    if "earbuds" in blob or "headphones" in blob or "audio" in blob:
        return "earbuds review: calls, gaming latency, and battery life"
    if "wearable" in blob or "smart ring" in blob or "smartwatch" in blob:
        return "wearable tech review: smart ring vs smartwatch value"
    if "ces" in blob or "mwc" in blob:
        return "new tech launch roundup: what is actually worth watching"
    return _short_topic(title, "Tech Reviews")


def _trend_query(niche: str, intent: str = "") -> str:
    kind = _niche_kind(niche)
    if kind == "tech":
        return (
            "latest 2026 consumer tech review trends AI phones foldable phones laptops "
            "earbuds wearables camera phones buyer questions price battery performance "
            f"{intent}"
        )
    return (
        f"{niche} latest product trends buyer questions comparison topics "
        f"new launches problems worth it review ideas {intent}"
    )


def _trend_queries(niche: str, intent: str = "") -> List[str]:
    kind = _niche_kind(niche)
    if kind == "tech":
        return [
            _trend_query(niche, intent),
            "2026 smartphone trends AI phones foldables camera phones battery price review",
            "2026 consumer tech launches laptops earbuds wearables buyer guide review",
        ]
    return [_trend_query(niche, intent)]


def _is_live_trend_result(niche: str, title: str, url: str, snippet: str) -> bool:
    kind = _niche_kind(niche)
    blob = f"{title} {url} {snippet}".lower()
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
        "shopify",
        "examples and trends",
        "youtube channels to watch",
        "about press copyright",
        "privacy policy",
        "terms",
        "amazon.",
        "flipkart.",
        "best prices",
        "buy mobile phones online",
        "coupon",
        "deals",
        "crypto",
        "nft",
        "blockchain",
        "insurance",
        "foundation partners",
        "youtube.com",
        "tiktok.com",
        "latest & new smartphones",
        "list of all",
    )
    if not title or any(term in blob for term in blocked):
        return False
    if kind != "tech":
        return True

    tech_terms = (
        "phone", "smartphone", "android", "iphone", "foldable", "laptop", "macbook",
        "earbuds", "headphones", "wearable", "smartwatch", "smart ring", "camera",
        "battery", "chip", "snapdragon", "mediatek", "intel", "amd", "artificial intelligence",
        "ai phone", "ai-powered", "ces", "mwc", "gadget", "tablet", "vr", "ar", "console",
    )
    review_terms = (
        "review", "tested", "best", "buy", "price", "worth", "guide", "launch",
        "announced", "hands-on", "comparison", "durability", "repair", "battery",
        "performance", "buyers", "buying", "trend", "trends", "forecast",
    )
    return any(term in blob for term in tech_terms) and any(term in blob for term in review_terms)


def _trend_context(niche: str, intent: str = "") -> List[Dict[str, str]]:
    lower_niche = niche.lower()
    if (
        "gaming" in lower_niche
        or "game" in lower_niche
        or "gamer" in lower_niche
        or "esports" in lower_niche
        or "cook" in lower_niche
        or "food" in lower_niche
        or "recipe" in lower_niche
        or "fitness" in lower_niche
        or "workout" in lower_niche
        or "education" in lower_niche
        or "study" in lower_niche
        or "beauty" in lower_niche
        or "fashion" in lower_niche
        or "finance" in lower_niche
        or "money" in lower_niche
    ):
        return _fallback_trends(niche)

    results = []
    for query in _trend_queries(niche, intent):
        try:
            results.extend(search_web(query, max_results=8))
        except Exception:
            continue

    trends = []
    for result in results:
        title = _clean_text(result.get("title"))
        url = _clean_text(result.get("url"))
        snippet = _clean_text(result.get("snippet"))
        if not _is_live_trend_result(niche, title, url, snippet):
            continue
        topic = _tech_review_topic(title, snippet) if _niche_kind(niche) == "tech" else _short_topic(title, niche)
        if ".com" in topic.lower() or "/" in topic:
            continue
        if any(topic.lower() == item["topic"].lower() for item in trends):
            continue
        trends.append({
            "topic": topic,
            "name": topic,
            "title": title,
            "url": url,
            "snippet": snippet or _fallback_reason(niche, topic),
            "score": 95 - (len(trends) * 7),
        })
        if len(trends) >= 5:
            break

    if len(trends) < 3:
        for item in _fallback_trends(niche):
            if any(item["topic"].lower() == trend["topic"].lower() for trend in trends):
                continue
            trends.append(item)
            if len(trends) >= 5:
                break

    return trends


def _trend_sources(trends: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": item.get("title", item.get("topic", "")), "url": item.get("url", "")}
        for item in trends
        if item.get("url")
    ]


def _weekly_task_copy(content_type: str, primary: str, secondary: str, third: str, lang: str) -> Dict[str, Dict[str, str]]:
    copy = {
        "recipe": {
            "video": "Record a complete recipe video with final dish first, ingredients, cooking checkpoints, and plating.",
            "short": "Make a 30-45 second Short showing the final dish, 3 fast steps, and one taste/texture close-up.",
            "seo": "Create 3 title options, a food close-up thumbnail, description, tags, and pinned comment.",
        },
        "gaming": {
            "video": "Record gameplay proof, show the exact setting/mistake, then explain how viewers can copy it.",
            "short": "Make a 30-45 second Short with one clutch moment, one setting tip, and one result caption.",
            "seo": "Create a gameplay thumbnail, 3 searchable titles, tags, and a pinned question for the next guide.",
        },
        "fitness": {
            "video": "Film the routine with form checks, beginner mistakes, and a simple 7-day progression.",
            "short": "Make a quick form-fix Short with one mistake, one correction, and one visible result.",
            "seo": "Write titles around routine, mistake, and beginner result; use a posture-focused thumbnail.",
        },
        "education": {
            "video": "Teach the topic with one rule, two examples, and one practice question viewers can answer.",
            "short": "Make a 30-second memory trick or exam mistake Short with a clear answer reveal.",
            "seo": "Write titles around explained simply, exam mistake, and fast revision; use a board/notebook thumbnail.",
        },
        "beauty": {
            "video": "Show the before, step-by-step application or styling, mistakes to avoid, and final look.",
            "short": "Make a before-after Short with one product/step, one mistake, and the finished look.",
            "seo": "Write titles around beginner guide, affordable routine, and mistake fix; use a clean before-after thumbnail.",
        },
        "finance": {
            "video": "Explain the money topic with one simple example, numbers on screen, and one action step.",
            "short": "Make a 30-second money mistake Short with one number, one rule, and one next action.",
            "seo": "Write titles around explained simply, money mistake, and starter plan; use a clean number-based thumbnail.",
        },
        "review": {
            "video": f"Turn '{primary}' into a decision-first review: who should care, what to test, and who should skip.",
            "short": "Cut one proof moment: price shock, camera sample, battery result, repair risk, or before-after test.",
            "seo": "Write titles around viewer decision, real test result, and upgrade/buying mistake.",
        },
        "general": {
            "video": "Create a step-by-step video with one clear result, proof example, and viewer action.",
            "short": "Make a quick result-first Short with one tip, one example, and one question.",
            "seo": "Write titles around step-by-step guide, beginner mistake, and simple method.",
        },
    }
    return copy.get(content_type, copy["general"])


def _task_guide_steps(content_type: str, title: str, trend: str, secondary: str, lang: str, pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    scripts = pack["scripts"]
    if content_type == "review":
        return [
            {
                "stepNum": 1,
                "title": "Find the buyer question",
                "timestamp": "Planning",
                "duration": "20 min",
                "what": f"Turn '{trend}' into one viewer question: buy now, wait, upgrade, repair, choose cheaper, or avoid.",
                "script": f"Today I am checking {trend} from a normal buyer's point of view.",
                "onScreen": "Show the device/category, price or problem, and the final test result immediately.",
                "tip": "A tech review feels smarter when it answers a real buying decision, not just a topic.",
            },
            {
                "stepNum": 2,
                "title": "Open with the result",
                "timestamp": "0:00 - 0:15",
                "duration": "30 min",
                "what": "Show the result first, then say what you tested.",
                "script": scripts["hook"],
                "onScreen": "Use a camera sample, battery number, speed test, price card, repair score, or side-by-side result.",
                "tip": "Viewers stay longer when the proof starts before the explanation.",
            },
            {
                "stepNum": 3,
                "title": "Run three viewer tests",
                "timestamp": "0:15 - 3:00",
                "duration": "90 min",
                "what": f"Test '{trend}' against '{secondary}' using 3 criteria viewers care about: price, daily use, and hidden tradeoff.",
                "script": "Test one is daily use. Test two is the hidden tradeoff. Test three is whether the price makes sense.",
                "onScreen": "Use score cards, close-ups, screen recordings, sample shots, benchmarks, or battery/cost captions.",
                "tip": "Show evidence on screen. Do not just say the opinion.",
            },
            {
                "stepNum": 4,
                "title": "Package the decision",
                "timestamp": "Upload",
                "duration": "45 min",
                "what": "Create a title and thumbnail that make the viewer decision obvious.",
                "script": scripts["finish"],
                "onScreen": "Thumbnail: device/category plus one result word like WAIT, BUY, SKIP, or TESTED.",
                "tip": "The title should say the decision; the thumbnail should show the proof or conflict.",
            },
        ]

    guide_map = {
        "fitness": {
            "step1": ("Choose the visible result", f"Turn '{trend}' into one beginner-safe result: better form, more consistency, or a simple 7-day routine.", "Show the exercise result or form correction first.", "People trust fitness videos when the movement looks clear and achievable."),
            "step2": ("Teach the setup", "Explain starting position, reps/time, rest, and the easiest beginner version.", "Use full-body framing, rep counter, and form arrows.", "Good form beats intensity for beginner content."),
            "step3": ("Correct the mistake", f"Show the most common mistake for '{trend}' and the exact correction.", "Split screen: wrong form vs correct form.", "One form correction can become a strong Short."),
            "step4": ("Finish with progression", "Give viewers a simple 7-day plan and ask them to report results.", "Show day-by-day checklist and final posture/result.", "Make the next action small enough to start today."),
        },
        "education": {
            "step1": ("Pick one learning promise", f"Turn '{trend}' into one clear lesson promise: understand, remember, solve, or revise.", "Show the final solved example or exam-style question first.", "Students stay when they know what they will be able to do by the end."),
            "step2": ("Explain the core rule", "Teach the one rule or idea that unlocks the topic.", "Board/notebook view with one highlighted formula or rule.", "Keep the first explanation simple before adding exceptions."),
            "step3": ("Work through examples", f"Use two examples for '{trend}': one easy and one exam-style.", "Write each step clearly and pause on the answer.", "Examples make education content feel useful, not theoretical."),
            "step4": ("Add practice and recap", "End with a practice question, answer hint, and short recap.", "Show question on screen and ask viewers to comment the answer.", "A comment question gives you the next video idea."),
        },
        "beauty": {
            "step1": ("Show the before-after promise", f"Make '{trend}' visual immediately with a before shot and the final look.", "Show the final face/outfit/hair result in the first seconds.", "Beauty content needs the result on screen fast."),
            "step2": ("Build the base", "Show the first product, prep step, or styling choice that affects the final result most.", "Clean close-ups, product names, and shade/step captions.", "Keep lighting consistent so the change is believable."),
            "step3": ("Fix the common mistake", f"Show the mistake beginners make with '{trend}' and the cleaner alternative.", "Side-by-side mistake vs corrected step.", "Mistake content is highly saveable when the fix is simple."),
            "step4": ("Finish the look", "Reveal the final result and give one affordable swap or routine tip.", "Final before-after, product/routine list, and comment question.", "Ask viewers what look or product they want tested next."),
        },
        "finance": {
            "step1": ("Choose the money problem", f"Turn '{trend}' into one practical problem: save, invest, budget, avoid debt, or understand risk.", "Show the key number or result first.", "Finance content works when the viewer sees a concrete number."),
            "step2": ("Explain the simple rule", "Break the topic into one rule with plain language.", "Use a clean table, calculator, or simple chart.", "Avoid jargon until the basic idea is clear."),
            "step3": ("Show a real example", f"Use a realistic example for '{trend}' with numbers viewers can copy.", "Show income/expense/investment numbers step by step.", "Numbers make advice feel practical and trustworthy."),
            "step4": ("Give the next action", "End with one safe next step and one mistake to avoid.", "Checklist: do this today, avoid this, ask this next.", "Do not overpromise returns. Keep the advice practical."),
        },
        "general": {
            "step1": ("Choose the clear result", f"Turn '{trend}' into one result viewers can understand immediately.", "Show the final result or strongest example first.", "One clear promise beats a broad topic."),
            "step2": ("Show the simple setup", "Explain what viewers need before they start.", "Show tools, checklist, or first step on screen.", "Remove anything that does not support the promise."),
            "step3": ("Prove the method", "Walk through the method with one concrete example.", "Use captions for each step and show progress.", "A visible example makes the guide easier to follow."),
            "step4": ("Package the next action", "End with a recap, title promise, and comment question.", "Show final result plus the next action.", "Use comments to choose the next guide."),
        },
    }
    guide = guide_map.get(content_type, guide_map["general"])
    script_keys = ["hook", "setup", "proof", "finish"]
    return [
        {
            "stepNum": index + 1,
            "title": guide[f"step{index + 1}"][0],
            "timestamp": ["Planning", "0:00 - 0:20", "0:20 - 2:30", "Upload"][index],
            "duration": ["20 min", "30 min", "75 min", "40 min"][index],
            "what": guide[f"step{index + 1}"][1],
            "script": scripts[script_keys[index]],
            "onScreen": guide[f"step{index + 1}"][2],
            "tip": guide[f"step{index + 1}"][3],
        }
        for index in range(4)
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
    content_type = pack["content_type"]
    task_copy = _weekly_task_copy(content_type, primary, secondary, third, lang)

    tasks = [
        {
            "id": "idea-1",
            "type": "video",
            "title": f"Create: {primary}",
            "detail": task_copy["video"],
            "time": "2-3 hours",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[0].get("snippet") or f"This topic appeared in current {niche} trend research.",
        },
        {
            "id": "short-1",
            "type": "short",
            "title": f"Short: {secondary}",
            "detail": task_copy["short"],
            "time": "60 min",
            "priority": "high",
            "isIdea": True,
            "trendReason": trends[1].get("snippet") if len(trends) > 1 else "",
        },
        {
            "id": "thumb-1",
            "type": "seo",
            "title": f"Package: {third}",
            "detail": task_copy["seo"],
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
    primary = trends[0]["topic"] if trends else niche
    secondary = trends[1]["topic"] if len(trends) > 1 else f"{niche} comparison"
    pack = _content_pack(niche, primary, secondary, lang)
    pack_titles = _pack_titles(pack)

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
            f"Hi. I am TubeCoach for your {niche} channel.\n\n"
            f"Best topic to work on now: {primary}.\n"
            f"Suggested title: {pack_titles[0] if pack_titles else primary}\n"
            f"Opening hook: show the result or verdict first, then explain the proof in {lang}.\n"
            f"Next action: ask me for a full script, SEO pack, thumbnail idea, or weekly plan."
        )
        sources = _trend_sources(trends)
    else:
        trend_lines = "\n".join([f"- {item['topic']}" for item in trends[:3]])
        title_lines = "\n".join([f"- {title}" for title in pack_titles[:3]])
        tag_line = ", ".join(pack.get("tags", [])[:8])
        answer_text = (
            f"TubeCoach recommendation for {niche}:\n\n"
            f"{trend_lines}\n\n"
            f"For '{task_title or research_question}', use this exact plan:\n"
            f"1. Hook: show the final result, verdict, or comparison in the first 5 seconds.\n"
            f"2. Proof: cover 3 viewer-first points from '{primary}'.\n"
            f"3. Decision: clearly say who should try it, buy it, skip it, or comment.\n"
            f"4. Short: cut the strongest proof moment into a 20-45 second Short.\n\n"
            f"Titles:\n{title_lines}\n\n"
            f"Description:\n{pack.get('description')}\n\n"
            f"Tags: {tag_line}\n\n"
            f"Thumbnail: {pack.get('thumbnail')}\n\n"
            f"Pinned comment: {pack.get('pinnedComment') or pack.get('first_comment')}"
        ).strip()
        sources = _trend_sources(trends)

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
    requested_topic = re.sub(r"^(Create|Short|Package):\s*", "", _clean_text(title), flags=re.I)
    trend_topics = [item["topic"] for item in trends]
    trend = requested_topic if requested_topic and requested_topic not in {"TubeCoach task", "Script+SEO"} else trends[0]["topic"]
    if trend not in trend_topics:
        trends = [{
            "topic": trend,
            "name": trend,
            "title": trend,
            "url": "",
            "snippet": _fallback_reason(niche, trend),
            "score": 96,
        }] + trends
    secondary = next((item["topic"] for item in trends if item["topic"].lower() != trend.lower()), f"{niche} comparison")
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
        "totalTime": "3-4 hours" if pack["content_type"] == "review" else "2-3 hours",
        "steps": _task_guide_steps(pack["content_type"], title, trend, secondary, lang, pack),
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
