import json
from pathlib import Path

from native.config import NATIVE_TRAINING_PATH, PROJECT_ROOT, ensure_native_dirs


CORPUS_PATH = PROJECT_ROOT / "datasets" / "native_tubecoach.txt"


SEED_EXAMPLES = [
    {
        "input": {
            "niche": "Tech Reviews",
            "lang": "Tamil",
            "question": "Create a weekly YouTube plan",
            "notes": "Use buyer-decision topics with proof first.",
            "badOutput": "Generic AI smartphone features plan",
        },
        "target": {
            "summary": "Create one Tamil tech review around a real buyer decision, one proof-based Short, and one mobile-readable SEO package.",
            "tasks": [
                {
                    "title": "Foldable phone repair cost test for Tamil buyers",
                    "hook": "Do not buy a foldable phone until you see this repair-cost risk.",
                    "proof": ["price comparison", "durability risk", "who should buy or skip"],
                    "short": "Show the repair cost in the first 2 seconds.",
                },
                {
                    "title": "Camera phone low-light test",
                    "hook": "This camera looks good in daylight, but what happens at night?",
                    "proof": ["same scene photo", "video sample", "battery drain while recording"],
                },
            ],
            "seo": {
                "titles": ["Foldable Phone Repair Cost Test", "Before You Buy a Foldable Phone, Watch This", "Tamil Tech Review: Buy or Skip?"],
                "thumbnail": "Phone plus repair price, one word: WAIT?",
            },
        },
    },
    {
        "input": {
            "niche": "Gaming",
            "lang": "Tamil",
            "question": "Create a weekly YouTube plan",
            "notes": "Use gameplay proof, settings, and one beginner mistake.",
            "badOutput": "Repeated best settings title",
        },
        "target": {
            "summary": "Create one settings guide with live match proof, one clutch Short, and one readable gameplay thumbnail.",
            "tasks": [
                {
                    "title": "BGMI sensitivity settings with live match proof",
                    "hook": "If your aim shakes, copy this setting and test one match.",
                    "proof": ["settings screen", "before aim clip", "after fight replay"],
                },
                {
                    "title": "Free Fire headshot mistake fix",
                    "hook": "This one drag mistake is why beginners miss headshots.",
                    "proof": ["wrong movement", "correct movement", "one kill replay"],
                },
            ],
        },
    },
    {
        "input": {
            "niche": "Cooking",
            "lang": "Tamil",
            "question": "Create a weekly YouTube plan",
            "notes": "Show final dish first, ingredients, texture checkpoints, and shortcut.",
            "badOutput": "Generic cooking topic",
        },
        "target": {
            "summary": "Create one quick recipe with final dish first, one texture-check Short, and one recipe SEO package.",
            "tasks": [
                {
                    "title": "5-minute rava upma breakfast",
                    "hook": "Today I will show soft rava upma with no lumps.",
                    "proof": ["ingredients shot", "roasting texture", "final spoon close-up"],
                }
            ],
        },
    },
    {
        "input": {
            "niche": "Fitness",
            "lang": "English",
            "question": "Create a weekly YouTube plan",
            "notes": "Beginner-safe routine, form checks, and 7-day progression.",
            "badOutput": "Generic workout tips",
        },
        "target": {
            "summary": "Create one beginner routine, one form-fix Short, and one progression checklist.",
            "tasks": [
                {
                    "title": "Beginner push-up progression",
                    "hook": "If push-ups hurt your shoulders, fix this first.",
                    "proof": ["wrong form", "correct form", "7-day progression"],
                }
            ],
        },
    },
    {
        "input": {
            "niche": "Education",
            "lang": "English",
            "question": "Create a weekly YouTube plan",
            "notes": "Teach one rule, two examples, and one practice question.",
            "badOutput": "Generic study motivation",
        },
        "target": {
            "summary": "Create one simple lesson, one exam mistake Short, and one practice-comment prompt.",
            "tasks": [
                {
                    "title": "3-hour exam revision plan",
                    "hook": "If your exam is close, revise this way first.",
                    "proof": ["topic list", "timed blocks", "practice question"],
                }
            ],
        },
    },
    {
        "input": {
            "niche": "Beauty",
            "lang": "English",
            "question": "Create a weekly YouTube plan",
            "notes": "Use before-after proof and affordable steps.",
            "badOutput": "Generic fashion idea",
        },
        "target": {
            "summary": "Create one visual routine, one before-after Short, and one mistake-fix package.",
            "tasks": [
                {
                    "title": "Simple daily skincare routine",
                    "hook": "This is the simplest routine for a clean look.",
                    "proof": ["before", "steps", "after"],
                }
            ],
        },
    },
    {
        "input": {
            "niche": "Finance",
            "lang": "English",
            "question": "Create a weekly YouTube plan",
            "notes": "Use simple numbers, practical action, and safe wording.",
            "badOutput": "Generic money advice",
        },
        "target": {
            "summary": "Create one beginner money guide, one number-based Short, and one checklist.",
            "tasks": [
                {
                    "title": "Monthly budget plan for beginners",
                    "hook": "If your money disappears every month, use this simple split.",
                    "proof": ["income example", "expense split", "saving action"],
                }
            ],
        },
    },
]


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

    rows = SEED_EXAMPLES + rows
    while len(rows) < 32:
        rows = rows + rows

    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        for row in rows[:64]:
            f.write(format_example(row))
            f.write("\n")

    print(f"Native corpus written: {CORPUS_PATH}")
    print(f"Examples: {min(len(rows), 64)}")


if __name__ == "__main__":
    main()
