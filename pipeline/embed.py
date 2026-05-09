# pipeline/embed.py

import os
import hashlib
from sentence_transformers import SentenceTransformer
import chromadb

CLEAN_DIR = "datasets/clean"
DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_knowledge"


def get_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def chunk_text(text, size=900, overlap=150):
    sentences = text.replace("\n", " ").split(". ")

    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if len(current) + len(sentence) < size:
            current += sentence + ". "
        else:
            if len(current.strip()) > 100:
                chunks.append(current.strip())

            # overlap by keeping last part of previous chunk
            current = current[-overlap:] + " " + sentence + ". "

    if len(current.strip()) > 100:
        chunks.append(current.strip())

    return chunks


def run_embedding():
    print("\n[EMBED] Starting embedding pipeline...\n")

    if not os.path.exists(CLEAN_DIR):
        print(f"[EMBED] Missing folder: {CLEAN_DIR}")
        return

    files = os.listdir(CLEAN_DIR)

    if not files:
        print("[EMBED] No cleaned data found.")
        return

    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        COLLECTION_NAME
    )

    new_chunks = []
    new_ids = []
    seen_ids = set()

    for file in files:
        if not file.endswith(".txt"):
            continue

        path = os.path.join(CLEAN_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for chunk in chunks:
            chunk = chunk.strip()

            if len(chunk) < 100:
                continue

            chunk_id = get_hash(chunk)

            # avoid duplicates inside same run
            if chunk_id in seen_ids:
                continue

            seen_ids.add(chunk_id)

            # avoid duplicates already inside ChromaDB
            existing = collection.get(ids=[chunk_id])

            if existing and existing["ids"]:
                continue

            new_chunks.append(chunk)
            new_ids.append(chunk_id)

    if not new_chunks:
        print("[EMBED] No new data to add.")
        return

    print(f"[EMBED] New chunks: {len(new_chunks)}")

    embeddings = model.encode(
        new_chunks,
        show_progress_bar=True
    ).tolist()

    collection.add(
        documents=new_chunks,
        embeddings=embeddings,
        ids=new_ids
    )

    print("\n[EMBED] Done! Vector DB updated.\n")


if __name__ == "__main__":
    run_embedding()