from typing import Any, Dict, List


def _clean(value: Any, fallback: str = "") -> str:
    return " ".join(str(value or fallback).strip().split())


def _is_creator_niche(niche: str) -> bool:
    lower = _clean(niche).lower()
    return any(term in lower for term in (
        "youtube",
        "creator",
        "tube",
        "tech review",
        "gaming",
        "cooking",
        "fitness",
        "education",
        "beauty",
        "finance",
    ))


def self_questions(prompt: str, niche: str = "content creation") -> List[str]:
    prompt = _clean(prompt)
    niche = _clean(niche, "content creation")
    if not prompt:
        return []

    if not _is_creator_niche(niche):
        return [
            f"What is the user really asking with '{prompt}'?",
            f"What fresh facts or sources would make the answer more accurate?",
            f"What mistake or outdated assumption should I avoid?",
        ]

    return [
        f"Why does '{prompt}' matter for a {niche} creator right now?",
        f"What proof or example would make '{prompt}' more trustworthy?",
        f"What should a beginner avoid when acting on '{prompt}'?",
    ]


def user_followups(prompt: str, niche: str = "content creation") -> List[str]:
    prompt = _clean(prompt)
    niche = _clean(niche, "content creation")
    if not prompt:
        if _is_creator_niche(niche):
            return [
                f"What is your exact {niche} goal this week?",
                "Do you want a short answer, full plan, or script?",
                "Should I optimize for views, subscribers, or sales?",
            ]
        return ["Do you want a quick answer or detailed answer?"]

    if not _is_creator_niche(niche):
        return [
            "Do you want a quick answer, detailed explanation, or step-by-step help?",
            "Should I remember this topic for future answers?",
        ]

    return [
        f"What result do you want from '{prompt}': views, subscribers, comments, or sales?",
        "Do you want the answer in simple steps, full script, or SEO package?",
        f"Should I remember your preference for future {niche} answers?",
    ]


def curiosity_summary(prompt: str, niche: str, learned_count: int) -> Dict[str, Any]:
    return {
        "selfQuestions": self_questions(prompt, niche),
        "askUserNext": user_followups(prompt, niche),
        "learnedSignals": learned_count,
    }
