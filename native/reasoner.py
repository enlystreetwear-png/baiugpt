from typing import Any, Dict, List

from native.config import NATIVE_AUTO_ONLINE_LEARN, NATIVE_AUTO_REBUILD_DATASET, NATIVE_ENABLED
from native.curiosity import curiosity_summary, self_questions, user_followups
from native.memory import memory_stats, relevant_memories
from native.online_learning import learn_online, should_learn_online


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
    status["autoUpdate"] = {
        "onlineLearning": NATIVE_AUTO_ONLINE_LEARN,
        "datasetRebuild": NATIVE_AUTO_REBUILD_DATASET,
        "weightTraining": "manual-or-scheduled",
        "reason": "GPU training after every chat would slow the app and can learn bad data.",
    }
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


def _intent(prompt: str) -> str:
    text = _clean(prompt).lower().strip(" ?!.")
    if text in {"hi", "hello", "hey", "hai", "yo", "good morning", "good evening", "good afternoon"}:
        return "greeting"
    if text in {"what is happening here", "what is happening", "what are you doing"}:
        return "meta"
    if text in {"who are you", "what are you", "what is baiugpt"}:
        return "identity"
    return "task"


def _general_chat_answer(prompt: str, niche: str, lang: str, learned: Dict[str, Any]) -> Dict[str, Any]:
    intent = _intent(prompt)
    memories = _memory_note(niche)
    if intent == "greeting":
        answer = (
            f"Hi. I am BaiuGPT, running locally on your PC with native mode.\n\n"
            "I can help with general questions, YouTube planning, tech research, scripts, coding ideas, and learning from your feedback. "
            "Ask me normally; I will only search online when the question is worth updating memory."
        )
    elif intent == "meta":
        answer = (
            "You are chatting with BaiuGPT native mode.\n\n"
            "Earlier it was treating every message like a TubeCoach planning task. I now separate greetings, meta chat, general questions, "
            "and creator-planning prompts. Useful questions can trigger online learning; low-value prompts will not pollute memory."
        )
    elif intent == "identity":
        answer = (
            "I am BaiuGPT, your local AI assistant. This version runs from your BaiuGPT server, uses your local memory/training files, "
            "and detects your RTX GPU for training workflows."
        )
    else:
        answer = ""

    if answer:
        return {
            "answer": f"{answer}\n\nLanguage: {lang}\n{memories}",
            "sources": learned.get("sources", []),
            "native": native_status(),
            "learning": learned,
            "curiosity": curiosity_summary(prompt, niche, learned.get("learned", 0)),
        }
    return {}


def _source_signal_lines(learned: Dict[str, Any]) -> List[str]:
    signals = learned.get("signals") or []
    lines = []
    for item in signals[:5]:
        title = _clean(item.get("title"))
        snippet = _clean(item.get("snippet"))
        if title and snippet:
            lines.append(f"- {title}: {snippet}")
        elif title:
            lines.append(f"- {title}")
    return lines


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
    learned = learn_online(prompt, niche=niche, lang=lang, deep=True) if should_learn_online(prompt) else {
        "status": "skipped",
        "reason": "low-value chat prompt",
        "learned": 0,
        "sources": [],
    }
    chat = _general_chat_answer(prompt, niche, lang, learned)
    if chat:
        return chat

    memories = _memory_note(niche)
    self_qs = self_questions(prompt, niche)
    followups = user_followups(prompt, niche)
    is_creator_niche = any(term in niche.lower() for term in ("youtube", "creator", "tech review", "gaming", "cooking", "fitness", "education", "beauty", "finance"))
    heading = f"BaiuGPT native plan for {niche}" if is_creator_niche else "BaiuGPT native answer"
    main_decision = (
        f"turn '{prompt}' into one viewer promise"
        if is_creator_niche else
        f"answer '{prompt}' with clear reasoning, useful examples, and a practical next step"
    )
    signal_lines = _source_signal_lines(learned)
    if is_creator_niche:
        answer = (
            f"{heading}:\n\n"
            f"1. Main decision: {main_decision}.\n"
            f"2. Why check: {self_qs[0] if self_qs else 'Why does this matter now?'}\n"
            f"3. Proof check: {self_qs[1] if len(self_qs) > 1 else 'What proof makes this trustworthy?'}\n"
            f"4. Risk check: {self_qs[2] if len(self_qs) > 2 else 'What should beginners avoid?'}\n"
            "5. Action: give the answer first, show 3 useful evidence points, then give a clear next step.\n"
            "6. Source use: keep short source notes and URLs instead of copying full pages.\n"
            "7. Learning: save feedback so future answers improve.\n\n"
            "Questions for you:\n"
            + "\n".join(f"- {question}" for question in followups)
            + "\n\n"
            f"Language: {lang}\n{memories}\n"
            f"Online learning: saved {learned.get('learned', 0)} new source signals."
        )
    else:
        answer = (
            f"{heading}:\n\n"
            f"You asked: {prompt}\n\n"
            "What I can do now: I searched for useful source signals, saved the clean notes locally, and rebuilt the local training dataset automatically.\n\n"
            "What I found:\n"
            + ("\n".join(signal_lines) if signal_lines else "- No strong new source signal was needed for this prompt.")
            + "\n\n"
            "My current answer: use the source links as fresh context, then ask me for the exact format you want: quick answer, detailed explanation, comparison table, code, script, or step-by-step plan.\n\n"
            "Self-checks I used:\n"
            + "\n".join(f"- {question}" for question in self_qs)
            + "\n\n"
            "Questions for you:\n"
            + "\n".join(f"- {question}" for question in followups)
            + "\n\n"
            f"Language: {lang}\n{memories}\n"
            f"Online learning: saved {learned.get('learned', 0)} new source signals."
        )
    return {
        "answer": answer,
        "sources": learned.get("sources", []),
        "native": native_status(),
        "learning": learned,
        "curiosity": curiosity_summary(prompt, niche, learned.get("learned", 0)),
    }
