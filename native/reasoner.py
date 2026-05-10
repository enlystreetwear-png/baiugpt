from typing import Any, Dict, List

from native.config import NATIVE_ENABLED
from native.memory import memory_stats, relevant_memories


def _clean(value: Any, fallback: str = "") -> str:
    text = " ".join(str(value or fallback).strip().split())
    return text


def _niche(profile: Dict[str, Any], fallback: str = "content creation") -> str:
    return _clean(profile.get("nicheDesc") or profile.get("niche"), fallback)


def _lang(profile: Dict[str, Any], fallback: str = "English") -> str:
    return _clean(profile.get("lang"), fallback)


def _device_status() -> Dict[str, Any]:
    try:
        import torch

        cuda = torch.cuda.is_available()
        return {
            "torchAvailable": True,
            "cudaAvailable": cuda,
            "device": "cuda" if cuda else "cpu",
            "gpuName": torch.cuda.get_device_name(0) if cuda else None,
            "gpuCount": torch.cuda.device_count() if cuda else 0,
        }
    except Exception as exc:
        return {
            "torchAvailable": False,
            "cudaAvailable": False,
            "device": "cpu",
            "gpuName": None,
            "gpuCount": 0,
            "error": str(exc),
        }


def native_status() -> Dict[str, Any]:
    status = {
        "enabled": NATIVE_ENABLED,
        "mode": "native-local",
        "providers": {
            "openai": False,
            "claude": False,
            "ollama": False,
            "hostedModels": False,
        },
        "device": _device_status(),
    }
    status.update(memory_stats())
    return status


def _creator_goal_from_snapshots(snapshots: List[Dict[str, Any]]) -> str:
    if not snapshots:
        return "No analytics yet, so focus on creating a strong first repeatable signal."
    latest = snapshots[-1]
    subs = latest.get("subscribers") or latest.get("subscriberCount") or 0
    views = latest.get("views") or latest.get("viewCount") or 0
    videos = latest.get("videos") or latest.get("videoCount") or 0
    return f"Current baseline: {subs} subscribers, {views} views, {videos} videos. Choose ideas that can create measurable CTR, retention, and comments this week."


def _memory_note(niche: str) -> str:
    memories = relevant_memories(niche)
    better = [_clean(row.get("notes") or row.get("question")) for row in memories if row.get("notes") or row.get("question")]
    if not better:
        return "No saved feedback yet. Learn from this response after the user rates it."
    return "Saved learning: " + " | ".join(better[-3:])


def _make_task_smarter(task: Dict[str, Any], niche: str, lang: str, trend_index: int) -> Dict[str, Any]:
    task = dict(task)
    title = _clean(task.get("title"))
    detail = _clean(task.get("detail"))
    if task.get("type") == "video":
        task["detail"] = (
            f"{detail} Add a real proof plan: 1 hook, 3 evidence points, 1 viewer decision, "
            f"and 1 Short cut from the strongest moment. Speak in {lang}."
        )
    elif task.get("type") == "short":
        task["detail"] = (
            f"{detail} Make the first 2 seconds show the result, then use one captioned proof point and one comment question."
        )
    elif task.get("type") == "seo":
        task["detail"] = (
            f"{detail} Create one curiosity title, one searchable title, and one mistake/decision title. "
            "Thumbnail must be readable on mobile."
        )
    elif task.get("type") == "engage":
        task["detail"] = f"{detail} Save the winning comment as the next training signal for BaiuGPT."

    task["nativeReason"] = (
        f"BaiuGPT native reasoning matched this task to {niche}, ranked it #{trend_index + 1}, "
        "and optimized it for hook, proof, package, and feedback learning."
    )
    if title and not task.get("title", "").startswith(("Create:", "Short:", "Package:", "Ask")):
        task["title"] = title
    return task


def refine_weekly_plan(payload: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    if not NATIVE_ENABLED or not isinstance(base, dict) or base.get("error"):
        return base

    profile = payload.get("profile", {}) or {}
    snapshots = payload.get("snapshots", []) or []
    niche = _niche(profile)
    lang = _lang(profile)
    refined = dict(base)
    refined["tasks"] = [
        _make_task_smarter(task, niche, lang, index)
        for index, task in enumerate(base.get("tasks", []))
    ]
    refined["summary"] = f"{base.get('summary', '')} Native BaiuGPT used local reasoning and memory."
    refined["focus"] = (
        f"{base.get('focus', '')} {_creator_goal_from_snapshots(snapshots)} "
        f"{_memory_note(niche)}"
    ).strip()
    refined["native"] = {
        "mode": "local-native",
        "gpu": _device_status(),
        "learning": _memory_note(niche),
    }
    return refined


def refine_task_guide(payload: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    if not NATIVE_ENABLED or not isinstance(base, dict) or base.get("error"):
        return base

    profile = payload.get("profile", {}) or {}
    task = payload.get("task", {}) or {}
    niche = task.get("niche") or _niche(profile)
    lang = task.get("lang") or _lang(profile)
    refined = dict(base)
    steps = []
    for step in base.get("steps", []):
        step = dict(step)
        step["nativeCheck"] = (
            f"Before recording, verify this step has one visible proof point and one line that fits {lang} viewers."
        )
        steps.append(step)
    refined["steps"] = steps

    seo = dict(base.get("seoContent", {}))
    if seo:
        seo["nativePackagingRule"] = (
            "Title = viewer decision. Thumbnail = visual proof. Description = promise + steps + comment question."
        )
        refined["seoContent"] = seo

    refined["native"] = {
        "mode": "local-native",
        "niche": niche,
        "learning": _memory_note(niche),
        "gpu": _device_status(),
    }
    return refined


def native_answer(prompt: str, niche: str = "content creation", lang: str = "English") -> Dict[str, Any]:
    prompt = _clean(prompt, "Give me a creator plan")
    memories = _memory_note(niche)
    answer = (
        f"BaiuGPT native plan for {niche}:\n\n"
        f"1. Main decision: turn '{prompt}' into one viewer promise.\n"
        "2. Reasoning: choose the angle with the clearest proof, not the broadest topic.\n"
        "3. Script: open with the result, show 3 evidence points, then give a clear next action.\n"
        "4. SEO: create one searchable title, one curiosity title, and one mistake-based title.\n"
        "5. Learning: save viewer comments and your rating so I can improve the next output.\n\n"
        f"Language: {lang}\n{memories}"
    )
    return {"answer": answer, "sources": [], "native": native_status()}

