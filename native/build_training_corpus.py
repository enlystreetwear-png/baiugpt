import json
from pathlib import Path

from native.config import NATIVE_TRAINING_PATH, PROJECT_ROOT, ensure_native_dirs


CORPUS_PATH = PROJECT_ROOT / "datasets" / "native_tubecoach.txt"


def format_example(row):
    item = row.get("input", {})
    target = row.get("target", "")
    return (
        "<|user|>\n"
        f"Niche: {item.get('niche', 'content creation')}\n"
        f"Language: {item.get('lang', 'English')}\n"
        f"Question: {item.get('question', '')}\n"
        f"Notes: {item.get('notes', '')}\n"
        f"Bad output to improve: {json.dumps(item.get('badOutput'), ensure_ascii=False)}\n"
        "<|assistant|>\n"
        f"{json.dumps(target, ensure_ascii=False)}\n"
        "<|end|>\n"
    )


def main():
    ensure_native_dirs()
    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    if NATIVE_TRAINING_PATH.exists():
        with open(NATIVE_TRAINING_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue

    if not rows:
        seed = {
            "input": {
                "niche": "Tech Reviews",
                "lang": "Tamil",
                "question": "Create a weekly YouTube plan",
                "notes": "Make it niche-specific, trend-aware, and practical.",
                "badOutput": {},
            },
            "target": {
                "summary": "Create one buyer-decision tech review, one proof-based Short, and one mobile-readable SEO package.",
                "rules": ["Show result first", "Use 3 proof points", "End with buy/wait/skip decision"],
            },
        }
        rows = [seed]

    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(format_example(row))
            f.write("\n")

    print(f"Native corpus written: {CORPUS_PATH}")
    print(f"Examples: {len(rows)}")


if __name__ == "__main__":
    main()

