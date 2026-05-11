import hashlib
import time
from typing import Any, Dict, List

from native.config import NATIVE_AUTO_ONLINE_LEARN, NATIVE_MEMORY_PATH, NATIVE_TRAINING_PATH
from native.memory import append_jsonl, read_jsonl
from native.training_maintenance import rebuild_native_dataset
from research.research import search_web


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _fingerprint(*parts: Any) -> str:
    raw = "|".join(_clean(part).lower() for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _known_ids() -> set:
    rows = read_jsonl(NATIVE_MEMORY_PATH, limit=100000)
    return {row.get("id") for row in rows if row.get("id")}


def _safe_result(result: Dict[str, Any]) -> Dict[str, str]:
    title = _clean(result.get("title"))
    url = _clean(result.get("url"))
    snippet = _clean(result.get("snippet"))
    if len(snippet) > 420:
        snippet = snippet[:420].rsplit(" ", 1)[0] + "..."
    return {"title": title, "url": url, "snippet": snippet}


def should_learn_online(query: str) -> bool:
    query = _clean(query).lower().strip(" ?!.")
    if not query:
        return False
    greetings = {"hi", "hello", "hey", "hai", "yo", "ok", "thanks", "thank you"}
    if query in greetings:
        return False
    meta_prompts = {
        "what is happening here",
        "what is happening",
        "what are you doing",
        "who are you",
        "how are you",
    }
    if query in meta_prompts:
        return False
    if len(query.split()) < 3 and not any(char.isdigit() for char in query):
        return False
    return True


def _is_bad_source(item: Dict[str, str]) -> bool:
    blob = f"{item.get('title', '')} {item.get('url', '')} {item.get('snippet', '')}".lower()
    blocked = (
        "dictionary",
        "definition",
        "meaning of",
        "pronunciation",
        "synonym",
        "merriam-webster",
        "cambridge.org",
        "collinsdictionary",
        "thefreedictionary",
        "wikipedia",
        "microsoft lists",
        "microsoft 365",
        "to-do list",
        "task list",
        "happening now",
        "privacy policy",
        "terms of service",
    )
    return any(term in blob for term in blocked)


def _base_search_query(query: str, niche: str) -> str:
    q = query.lower()
    if any(term in q for term in ("phone", "phones", "mobile", "mobiles", "smartphone")) and any(term in q for term in ("rs", "₹", "under", "below", "29999", "30000")):
        return "best smartphones under 30000 India 2026 review price camera battery performance"
    return f"{query} {niche} latest facts trends guide examples"


def _deep_queries(query: str, niche: str) -> List[str]:
    q = query.lower()
    if any(term in q for term in ("phone", "phones", "mobile", "mobiles", "smartphone")):
        return [
            f"{query} best models India review camera battery performance",
            f"{query} comparison price specs pros cons",
            f"{query} buyer guide India latest",
        ]
    return [
        f"why {query} matters for {niche}",
        f"{query} common mistakes problems examples",
        f"{query} latest buyer questions audience pain points",
    ]


def learn_online(
    query: str,
    niche: str = "content creation",
    lang: str = "English",
    max_results: int = 5,
    deep: bool = False,
) -> Dict[str, Any]:
    query = _clean(query)
    niche = _clean(niche, )
    lang = _clean(lang)
    if not NATIVE_AUTO_ONLINE_LEARN:
        return {"status": "skipped", "reason": "BAIUGPT_AUTO_ONLINE_LEARN is disabled", "learned": 0, "sources": []}
    if not should_learn_online(query):
        return {"status": "skipped", "reason": "low-value chat prompt", "learned": 0, "sources": []}

    search_queries = [_base_search_query(query, niche)]
    if deep:
        search_queries.extend(_deep_queries(query, niche))

    try:
        results = []
        per_query = max(1, min(max_results, 3))
        for search_query in search_queries:
            results.extend(search_web(search_query, max_results=per_query))
    except Exception as exc:
        return {"status": "error", "error": str(exc), "learned": 0, "sources": []}

    known = _known_ids()
    learned = 0
    sources: List[Dict[str, str]] = []
    signals: List[Dict[str, str]] = []
    now = int(time.time())

    for raw in results:
        item = _safe_result(raw)
        if not item["title"] or not item["url"] or _is_bad_source(item):
            continue
        item_id = _fingerprint(query, item["title"], item["url"])
        if item_id in known:
            sources.append({"title": item["title"], "url": item["url"]})
            continue

        memory = {
            "id": item_id,
            "type": "online_learning",
            "createdAt": now,
            "query": query,
            "niche": niche,
            "lang": lang,
            "title": item["title"],
            "url": item["url"],
            "deep": deep,
            "notes": f"Online signal for '{query}': {item['snippet']}",
        }
        append_jsonl(NATIVE_MEMORY_PATH, memory)
        append_jsonl(NATIVE_TRAINING_PATH, {
            "type": "online_source_example",
            "createdAt": now,
            "input": {
                "niche": niche,
                "lang": lang,
                "question": query,
                "sourceTitle": item["title"],
                "sourceUrl": item["url"],
                "notes": "Use online source as short factual signal with URL. Do not copy full page text.",
            },
            "target": {
                "source": item["title"],
                "url": item["url"],
                "shortSignal": item["snippet"],
                "answerRule": "Use this as one cited signal, then reason with niche, audience, proof, and user feedback.",
            },
        })
        learned += 1
        sources.append({"title": item["title"], "url": item["url"]})
        signals.append(item)

    rebuild = rebuild_native_dataset() if learned else {"status": "skipped", "reason": "no new learning"}

    return {
        "status": "saved",
        "query": query,
        "niche": niche,
        "deep": deep,
        "learned": learned,
        "sources": sources,
        "signals": signals,
        "dataset": rebuild,
    }
