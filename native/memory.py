import json
import time
from typing import Any, Dict, List

from native.config import NATIVE_MEMORY_PATH, NATIVE_TRAINING_PATH, ensure_native_dirs


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def append_jsonl(path, record: Dict[str, Any]) -> None:
    ensure_native_dirs()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path, limit: int = 500) -> List[Dict[str, Any]]:
    ensure_native_dirs()
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows[-limit:]


def remember_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "type": "feedback",
        "createdAt": int(time.time()),
        "niche": _clean(payload.get("niche")),
        "lang": _clean(payload.get("lang")),
        "rating": payload.get("rating"),
        "question": _clean(payload.get("question")),
        "badOutput": payload.get("badOutput"),
        "betterOutput": payload.get("betterOutput"),
        "notes": _clean(payload.get("notes")),
    }
    append_jsonl(NATIVE_MEMORY_PATH, record)

    if payload.get("betterOutput"):
        append_jsonl(NATIVE_TRAINING_PATH, {
            "type": "supervised_example",
            "createdAt": record["createdAt"],
            "input": {
                "niche": record["niche"],
                "lang": record["lang"],
                "question": record["question"],
                "badOutput": record["badOutput"],
                "notes": record["notes"],
            },
            "target": payload.get("betterOutput"),
        })

    return {"status": "saved", "memoryPath": str(NATIVE_MEMORY_PATH), "trainingPath": str(NATIVE_TRAINING_PATH)}


def relevant_memories(niche: str = "", limit: int = 8) -> List[Dict[str, Any]]:
    rows = read_jsonl(NATIVE_MEMORY_PATH)
    niche_l = _clean(niche).lower()
    blocked = (
        "dictionary",
        "definition",
        "meaning of",
        "pronunciation",
        "synonyms",
        "happening now",
        "wikipedia",
        "microsoft lists",
        "microsoft 365",
        "to-do list",
        "task list",
    )
    rows = [
        row for row in rows
        if not any(term in f"{row.get('title', '')} {row.get('url', '')} {row.get('notes', '')}".lower() for term in blocked)
    ]
    if niche_l:
        matched = [row for row in rows if niche_l in _clean(row.get("niche")).lower()]
    else:
        matched = rows
    return matched[-limit:]


def memory_stats() -> Dict[str, Any]:
    return {
        "memoryCount": len(read_jsonl(NATIVE_MEMORY_PATH, limit=100000)),
        "trainingExampleCount": len(read_jsonl(NATIVE_TRAINING_PATH, limit=100000)),
        "memoryPath": str(NATIVE_MEMORY_PATH),
        "trainingPath": str(NATIVE_TRAINING_PATH),
    }
