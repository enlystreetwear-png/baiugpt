import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from native.reasoner import native_status


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 120_000
MAX_READ_LINES = 220


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_path(path: str = "") -> Path:
    raw = _clean(path).replace("/", os.sep)
    target = (PROJECT_ROOT / raw).resolve() if raw else PROJECT_ROOT.resolve()
    root = PROJECT_ROOT.resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path is outside BaiuGPT workspace")
    return target


def _line_numbered(text: str, start: int = 1, max_lines: int = MAX_READ_LINES) -> str:
    lines = text.splitlines()
    selected = lines[start - 1:start - 1 + max_lines]
    return "\n".join(f"{index:>4}: {line}" for index, line in enumerate(selected, start=start))


def list_files(path: str = "", limit: int = 120) -> Dict[str, Any]:
    target = _safe_path(path)
    if not target.exists():
        return {"error": "Path not found", "path": str(target)}
    if target.is_file():
        return {"path": str(target), "files": [str(target.relative_to(PROJECT_ROOT))]}

    files: List[str] = []
    for item in target.rglob("*"):
        if len(files) >= limit:
            break
        if item.is_file() and ".git" not in item.parts and "__pycache__" not in item.parts:
            files.append(str(item.relative_to(PROJECT_ROOT)))
    return {"path": str(target), "files": files, "count": len(files), "limit": limit}


def read_file(path: str, start: int = 1, max_lines: int = MAX_READ_LINES) -> Dict[str, Any]:
    target = _safe_path(path)
    if not target.exists() or not target.is_file():
        return {"error": "File not found", "path": str(target)}
    if target.stat().st_size > MAX_FILE_BYTES:
        return {"error": "File too large for chat read", "path": str(target), "size": target.stat().st_size}

    text = target.read_text(encoding="utf-8", errors="replace")
    return {
        "path": str(target.relative_to(PROJECT_ROOT)),
        "content": _line_numbered(text, start=max(1, start), max_lines=max_lines),
    }


def search_code(query: str, limit: int = 40) -> Dict[str, Any]:
    query = _clean(query)
    if not query:
        return {"error": "Search query required", "matches": []}

    try:
        result = subprocess.run(
            ["rg", "--line-number", "--no-heading", "--glob", "!claude-code-main/**", query, str(PROJECT_ROOT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        lines = [line for line in result.stdout.splitlines() if line.strip()][:limit]
    except Exception:
        lines = []
        for file in PROJECT_ROOT.rglob("*"):
            if len(lines) >= limit:
                break
            if not file.is_file() or ".git" in file.parts or "claude-code-main" in file.parts:
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for index, line in enumerate(text.splitlines(), start=1):
                if query.lower() in line.lower():
                    lines.append(f"{file.relative_to(PROJECT_ROOT)}:{index}:{line}")
                    if len(lines) >= limit:
                        break

    return {"query": query, "matches": lines, "count": len(lines)}


def project_summary() -> Dict[str, Any]:
    key_files = [
        "server.py",
        "core/model.py",
        "native/reasoner.py",
        "native/online_learning.py",
        "native/code_agent.py",
        "ui/chat.html",
        "ui/chat.js",
        "transformer.py",
        "NATIVE_MODE.md",
    ]
    existing = [path for path in key_files if (PROJECT_ROOT / path).exists()]
    return {
        "root": str(PROJECT_ROOT),
        "keyFiles": existing,
        "capabilities": [
            "FastAPI BaiuGPT API",
            "TubeCoach planning endpoints",
            "Native general chat",
            "Auto online learning memory",
            "Local training corpus/tokenization",
            "Read-only Claude-Code-like workspace tools",
        ],
        "native": native_status(),
    }


def _extract_after(prompt: str, command: str) -> str:
    return prompt[len(command):].strip()


def code_agent_answer(prompt: str) -> Dict[str, Any]:
    prompt = _clean(prompt)
    lower = prompt.lower()
    trace: List[Dict[str, Any]] = []

    if lower.startswith("/files"):
        data = list_files(_extract_after(prompt, "/files"))
        trace.append({"tool": "list_files", "result": data})
        answer = "Here are the files I found:\n" + "\n".join(f"- {item}" for item in data.get("files", [])[:80])
    elif lower.startswith("/read"):
        data = read_file(_extract_after(prompt, "/read"))
        trace.append({"tool": "read_file", "result": data})
        answer = data.get("content") or data.get("error", "No content")
    elif lower.startswith("/search"):
        data = search_code(_extract_after(prompt, "/search"))
        trace.append({"tool": "search_code", "result": data})
        answer = "Search matches:\n" + ("\n".join(data.get("matches", [])) or "No matches found.")
    else:
        summary = project_summary()
        trace.append({"tool": "project_summary", "result": summary})
        search_terms = [word for word in prompt.split() if len(word) > 4][:3]
        matches = []
        for term in search_terms:
            result = search_code(term, limit=8)
            trace.append({"tool": "search_code", "query": term, "result": result})
            matches.extend(result.get("matches", []))
        answer = (
            "BaiuGPT Code Agent is active in read-only mode.\n\n"
            "I can inspect this workspace like a Claude-Code-style assistant using:\n"
            "- /files [folder]\n"
            "- /read [file]\n"
            "- /search [text]\n\n"
            "Project capabilities:\n"
            + "\n".join(f"- {item}" for item in summary["capabilities"])
        )
        if matches:
            answer += "\n\nRelevant code signals:\n" + "\n".join(matches[:12])

    return {
        "answer": answer,
        "toolTrace": trace,
        "mode": "code-agent-read-only",
        "workspace": str(PROJECT_ROOT),
    }

