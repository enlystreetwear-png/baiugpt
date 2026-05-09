# pipeline/ingest.py

import os
import json
import requests
from bs4 import BeautifulSoup

RAW_DIR = "datasets/raw"
SOURCES_FILE = "pipeline/sources.json"

os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load_sources():
    if not os.path.exists(SOURCES_FILE):
        print(f"Missing sources file: {SOURCES_FILE}")
        return []

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_url(url: str) -> str:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        paragraphs = soup.find_all("p")

        text = "\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
        )

        return text if len(text) > 100 else ""

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def safe_filename(name: str, index: int) -> str:
    name = name.lower()
    name = name.replace(" ", "_")
    name = "".join(c for c in name if c.isalnum() or c == "_")

    if not name:
        name = f"source_{index}"

    return f"{index}_{name}.txt"


def run_ingestion():
    print("\n[INGEST] Starting data collection...\n")

    sources = load_sources()

    if not sources:
        print("[INGEST] No sources found.")
        return

    for i, source in enumerate(sources):
        name = source.get("name", f"source_{i}")
        url = source.get("url", "")

        if not url:
            print(f"[SKIPPED] Missing URL for {name}")
            continue

        text = fetch_url(url)

        if text:
            filename = safe_filename(name, i)
            file_path = os.path.join(RAW_DIR, filename)

            header = (
                f"SOURCE_NAME: {name}\n"
                f"SOURCE_URL: {url}\n"
                f"SOURCE_TYPE: {source.get('type', 'web')}\n\n"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(header + text)

            print(f"[SAVED] {name} -> {file_path}")

        else:
            print(f"[SKIPPED EMPTY] {name}")

    print("\n[INGEST] Done!\n")


if __name__ == "__main__":
    run_ingestion()