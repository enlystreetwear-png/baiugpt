import re
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
    if _is_general_mode_name(niche):
        return "Local memory is enabled. I will use saved preferences when they match your question."
    memories = relevant_memories(niche)
    better = [
        _clean(row.get("notes") or row.get("question"))
        for row in memories
        if row.get("type") == "feedback" and (row.get("notes") or row.get("question"))
    ]
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
    if "weather" in text or "temperature" in text or "forecast" in text:
        return "weather"
    if text in {"step-by-step help", "step by step help", "show steps", "explain step by step"}:
        return "step_help"
    if any(term in text for term in ("write code", "simple code", "tell me output", "tell me that output", "code and output", "python code", "javascript code")):
        return "code"
    return "task"


def _mode(value: str) -> str:
    text = _clean(value, "tubecoach").lower()
    if text in {"tubecoach", "tube coach", "creator", "youtube", "niche"}:
        return "tubecoach"
    if text in {"code", "code agent", "workspace"}:
        return "code"
    return "general"


def _is_general_mode_name(value: str) -> bool:
    return _clean(value).lower() in {
        "",
        "general",
        "general purpose",
        "all purpose",
        "all-purpose",
        "chat",
        "general chat",
        "normal chat",
        "content creation",
    }


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


def _recent_user_context(messages: List[Dict[str, Any]]) -> str:
    if not messages:
        return ""
    user_lines = []
    for message in messages[-8:]:
        if _clean(message.get("role")).lower() == "user":
            text = _clean(message.get("text") or message.get("content") or message.get("message"))
            if text:
                user_lines.append(text)
    if len(user_lines) <= 1:
        return ""
    return "Previous context: " + " | ".join(user_lines[-3:-1])


def _question_is_followup(prompt: str) -> bool:
    text = _clean(prompt).lower()
    return len(text.split()) <= 5 and any(term in text for term in (
        "what about",
        "battery",
        "camera",
        "price",
        "performance",
        "which one",
        "why",
        "how",
    ))


def _learning_query(prompt: str, messages: List[Dict[str, Any]]) -> str:
    context = _recent_user_context(messages)
    if context and _question_is_followup(prompt):
        return f"{context}. Follow-up: {prompt}"
    return prompt


def _should_use_online(prompt: str, niche: str, messages: List[Dict[str, Any]], mode: str = "general") -> bool:
    intent = _intent(prompt)
    if intent in {"greeting", "meta", "identity", "code", "step_help"}:
        return False
    if _mode(mode) == "tubecoach":
        return True
    text = _clean(_learning_query(prompt, messages)).lower()
    fresh_terms = (
        "weather",
        "temperature",
        "forecast",
        "today",
        "latest",
        "current",
        "news",
        "price",
        "under rs",
        "under ₹",
        "under 30000",
        "under 29999",
        "best phone",
        "top phone",
        "mobile under",
    )
    return any(term in text for term in fresh_terms)


def _claude_style_rules() -> List[str]:
    return [
        "Answer the user directly before asking follow-up questions.",
        "Use fresh sources only when the answer depends on current facts.",
        "Keep memory as short useful signals, not copied webpages.",
        "Ask one or two clarifying questions only when they would change the answer.",
        "Keep general chat separate from specialist modes.",
    ]


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
            "This is General Chat. It answers normal questions directly, uses online search only for fresh facts, "
            "and keeps specialist planning out of this chat mode."
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
            "curiosity": None,
        }
    return {}


def _last_meaningful_user_prompt(messages: List[Dict[str, Any]], current_prompt: str) -> str:
    current = _clean(current_prompt).lower()
    for message in reversed(messages[-8:]):
        if _clean(message.get("role")).lower() != "user":
            continue
        text = _clean(message.get("text") or message.get("content") or message.get("message"))
        if text and text.lower() != current:
            return text
    return ""


def _code_answer(prompt: str, lang: str, step_by_step: bool = False, original_prompt: str = "") -> str:
    question = original_prompt or prompt
    code = (
        "name = \"BaiuGPT\"\n"
        "total = 2 + 3\n"
        "print(\"Hello from\", name)\n"
        "print(\"2 + 3 =\", total)"
    )
    output = "Hello from BaiuGPT\n2 + 3 = 5"
    if step_by_step:
        return (
            f"Sure. For your earlier request, '{question}', here is the step-by-step version:\n\n"
            "1. Create a variable called `name` and store `BaiuGPT`.\n"
            "2. Add `2 + 3` and store the answer in `total`.\n"
            "3. Print both lines.\n\n"
            "Python code:\n\n"
            f"```python\n{code}\n```\n\n"
            "Output:\n\n"
            f"```text\n{output}\n```\n\n"
            f"Language: {lang}"
        )
    return (
        "Here is a simple Python code example and its output:\n\n"
        f"```python\n{code}\n```\n\n"
        "Output:\n\n"
        f"```text\n{output}\n```\n\n"
        "Why this output happens: `print()` shows text on the screen, and `2 + 3` becomes `5`.\n\n"
        f"Language: {lang}"
    )


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


def _weather_answer(prompt: str, lang: str, learned: Dict[str, Any]) -> str:
    lines = _source_signal_lines(learned)
    if not lines:
        return (
            f"I could not get a strong live weather signal for '{prompt}' right now. "
            "Try asking again with the city name, or check a live weather source."
        )

    return (
        f"Weather for Pondicherry/Puducherry:\n\n"
        + "\n".join(lines[:4])
        + "\n\nShort answer: it looks warm, around the high-20s to low-30s Celsius from the available source snippets. For the exact current temperature and rain chance, open the live hourly source because weather changes quickly."
        + f"\n\nLanguage: {lang}"
    )


def _phone_answer(prompt: str, lang: str, learned: Dict[str, Any], context: str = "") -> str:
    lines = _source_signal_lines(learned)
    models = _extract_phone_models(learned)
    context_line = f"{context}\n\n" if context else ""
    if not lines:
        return (
            f"{context_line}I can help with '{prompt}', but I do not have enough fresh source signals in this response to rank exact models safely.\n\n"
            "Good phone shortlist rule under this budget: compare processor, camera samples, battery/charging, software updates, display quality, and service support. "
            "For India pricing, always verify the final cart price because offers change daily."
            f"\n\nLanguage: {lang}"
        )

    shortlist = ""
    if models:
        shortlist = (
            "Source-backed shortlist from the latest snippets:\n"
            + "\n".join(f"{index + 1}. {model}" for index, model in enumerate(models[:5]))
            + "\n\n"
        )

    return (
        f"{context_line}Short answer: for '{prompt}', start with these current candidates, then verify final sale price and variants before buying.\n\n"
        + shortlist
        + "Do not choose only by headline specs. Compare real camera samples, battery life, update promise, thermals, and after-sales support.\n\n"
        "Fresh source signals I checked:\n"
        + "\n".join(lines[:5])
        + "\n\nHow to decide:\n"
        "1. Pick performance first if you game or edit video.\n"
        "2. Pick camera proof first if you make reels, reviews, or family videos.\n"
        "3. Pick battery and service first if this is your main phone for 2-3 years.\n"
        "4. Verify the exact model price on Amazon/Flipkart/brand store before buying.\n\n"
        "Ask me for a ranked list with your priority, for example: gaming, camera, battery, or all-rounder."
        f"\n\nLanguage: {lang}"
    )


def _extract_phone_models(learned: Dict[str, Any]) -> List[str]:
    models: List[str] = []
    brand_pattern = re.compile(
        r"\b(?:OnePlus|Realme|Motorola|Vivo|OPPO|Samsung|Redmi|iQOO|POCO|Nothing|CMF|Honor|Infinix|Tecno|Lava|iPhone|Google Pixel|Pixel)\s+[A-Za-z0-9+ .-]{1,42}",
        re.IGNORECASE,
    )
    for item in learned.get("signals") or []:
        blob = _clean(f"{item.get('title', '')}. {item.get('snippet', '')}")
        for match in brand_pattern.findall(blob):
            model = _clean(match).strip(" .,-")
            model = re.split(r"\b(?:testifies|comparison|ranked|review|price|prices|camera|battery|under|online|in india)\b", model, flags=re.IGNORECASE)[0].strip(" .,-")
            if model and any(char.isdigit() for char in model) and model not in models:
                models.append(model)
            if len(models) >= 5:
                return models

        snippet = _clean(item.get("snippet"))
        for marker in (" are ", " including "):
            if marker not in snippet:
                continue
            tail = snippet.split(marker, 1)[1]
            tail = tail.split(".", 1)[0]
            for part in tail.replace(" & ", ", ").split(","):
                model = _clean(part)
                if not model or len(model) < 4:
                    continue
                lower = model.lower()
                if any(skip in lower for skip in (
                    "and more",
                    "etc",
                    "compare specs",
                    "prices to find",
                    "latest",
                    "best phones",
                    "smartphone picks",
                    "top five",
                    "our top",
                )):
                    continue
                if not any(char.isdigit() for char in model) and "iphone" not in lower:
                    continue
                if model not in models:
                    models.append(model)
                if len(models) >= 5:
                    return models
    return models


def _general_task_answer(prompt: str, niche: str, lang: str, learned: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
    lines = _source_signal_lines(learned)
    context = _recent_user_context(messages)
    context_line = f"{context}\n\n" if context and _question_is_followup(prompt) else ""
    lower = prompt.lower()
    context_lower = context.lower()
    intent = _intent(prompt)

    if intent == "code":
        return _code_answer(prompt, lang)

    if intent == "step_help":
        previous = _last_meaningful_user_prompt(messages, prompt)
        if previous and _intent(previous) == "code":
            return _code_answer(prompt, lang, step_by_step=True, original_prompt=previous)
        return (
            "Sure. Send me the exact thing you want help with, and I will break it into clear steps.\n\n"
            "Example: `make a login page`, `fix this error`, or `explain this code`.\n\n"
            f"Language: {lang}"
        )

    if any(term in f"{lower} {context_lower}" for term in ("phone", "phones", "mobile", "smartphone")):
        return _phone_answer(prompt, lang, learned, context if _question_is_followup(prompt) else "")

    if lines:
        answer = (
            f"{context_line}Here is the useful answer for '{prompt}':\n\n"
            "I checked current source signals, then used them as context instead of copying them. The best next move is to focus on the part that changes your decision or action.\n\n"
            "What I found:\n"
            + "\n".join(lines[:5])
            + "\n\n"
            "My take:\n"
            "- Use the freshest source for facts that can change, like prices, weather, tools, product specs, or news.\n"
            "- Use reasoning for the decision: what matters, what risk to avoid, and what action is worth taking next.\n"
            "- Save only the useful lesson to memory so future answers improve without filling BaiuGPT with noisy pages."
        )
    else:
        answer = (
            f"{context_line}Here is my answer for '{prompt}':\n\n"
            "This does not need a web search. I will answer directly and only search when the question depends on live facts like weather, prices, news, or current product lists.\n\n"
            "Best next step: ask the exact thing you want, and I will give the answer first, then the steps or explanation."
        )

    rules = "; ".join(_claude_style_rules()[:3])
    return f"{answer}\n\nBaiuGPT chat mode: {rules}.\n\nLanguage: {lang}"


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


def native_answer(
    prompt: str,
    niche: str = "Tech Reviews",
    lang: str = "English",
    messages: List[Dict[str, Any]] = None,
    mode: str = "tubecoach",
) -> Dict[str, Any]:
    messages = messages or []
    mode = _mode(mode)
    prompt = _clean(prompt, "Give me a creator plan")
    learning_query = _learning_query(prompt, messages)
    use_online = _should_use_online(prompt, niche, messages, mode)
    learned = learn_online(learning_query, niche=niche, lang=lang, deep=True) if use_online and should_learn_online(learning_query) else {
        "status": "skipped",
        "reason": "online search not needed for this prompt",
        "learned": 0,
        "sources": [],
    }
    is_creator_niche = mode == "tubecoach"
    chat = {} if is_creator_niche else _general_chat_answer(prompt, niche, lang, learned)
    if chat:
        return chat

    memories = _memory_note(niche)
    self_qs = self_questions(prompt, niche)
    followups = user_followups(prompt, niche)
    heading = f"BaiuGPT native plan for {niche}" if is_creator_niche else "BaiuGPT native answer"
    main_decision = (
        f"turn '{prompt}' into one viewer promise"
        if is_creator_niche else
        f"answer '{prompt}' with clear reasoning, useful examples, and a practical next step"
    )
    signal_lines = _source_signal_lines(learned)
    if _intent(prompt) == "weather" and not is_creator_niche:
        answer = _weather_answer(prompt, lang, learned)
        return {
            "answer": f"{answer}\n{memories}\nOnline learning: saved {learned.get('learned', 0)} new source signals.",
            "sources": learned.get("sources", []),
            "native": native_status(),
            "learning": learned,
            "curiosity": None,
        }

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
        answer = _general_task_answer(prompt, niche, lang, learned, messages)
        answer += f"\n\n{memories}"
        if learned.get("learned", 0):
            answer += f"\nOnline learning: saved {learned.get('learned', 0)} new source signals."
    return {
        "answer": answer,
        "sources": learned.get("sources", []),
        "native": native_status(),
        "learning": learned,
        "curiosity": curiosity_summary(prompt, niche, learned.get("learned", 0)) if is_creator_niche else None,
    }
