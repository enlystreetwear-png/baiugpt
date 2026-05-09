# pipeline/clean.py

import os
import re

RAW_DIR = "datasets/raw"
CLEAN_DIR = "datasets/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)   # remove extra spaces
    text = re.sub(r"\n+", " ", text)   # remove new lines
    return text.strip()


def run_cleaning():
    print("\n[CLEAN] Cleaning raw data...\n")

    files = os.listdir(RAW_DIR)

    if not files:
        print("No raw data found.")
        return

    for file in files:
        path = os.path.join(RAW_DIR, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            cleaned = clean_text(text)

            out_path = os.path.join(CLEAN_DIR, file)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            print(f"[CLEANED] {file}")

        except Exception as e:
            print(f"Error cleaning {file}: {e}")

    print("\n[CLEAN] Done!\n")


if __name__ == "__main__":
    run_cleaning()