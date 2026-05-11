import hashlib
import time
from typing import Any, Dict, List

from native.config import NATIVE_AUTO_ONLINE_LEARN, NATIVE_MEMORY_PATH, NATIVE_TRAINING_PATH
from native.memory import append_jsonl, read_jsonl
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


def _deep_queries(query: str, niche: str) -> List[str]:
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
    if len(query) < 3:
        return {"status": "skipped", "reason": "query too short", "learned": 0, "sources": []}

    search_queries = [f"{query} {niche} latest facts trends guide examples"]
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
    now = int(time.time())

    for raw in results:
        item = _safe_result(raw)
        if not item["title"] or not item["url"]:
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

    return {
        "status": "saved",
        "query": query,
        "niche": niche,
        "deep": deep,
        "learned": learned,
        "sources": sources,
    }
