# research/research_agent.py

from sentence_transformers import SentenceTransformer
import chromadb
import hashlib

from research.web_search import search_web
from research.web_fetcher import fetch_page_text
from research.reasoner import make_research_answer


DB_PATH = "rag_db"
COLLECTION_NAME = "baiu_research"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

embed_model = SentenceTransformer(EMBED_MODEL_NAME)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    COLLECTION_NAME
)


# ==================================================
# SOURCE QUALITY RANKING
# ==================================================

def source_score(url):
    url = url.lower()

    high_quality = [
        "arxiv.org",
        "nature.com",
        "science.org",
        "springer.com",
        "stanford.edu",
        "mit.edu",
        "berkeley.edu",
        "openai.com",
        "deepmind.google",
        "ai.googleblog.com",
        "meta.com",
        "microsoft.com",
        "anthropic.com",
        "huggingface.co",
        "paperswithcode.com"
    ]

    medium_quality = [
        "wikipedia.org",
        "github.com",
        "ibm.com",
        "nvidia.com"
    ]

    low_quality = [
        "c-sharpcorner.com",
        "buildfastwithai.com",
        "medium.com",
        "towardsdatascience.com",
        "analyticsvidhya.com"
    ]

    for domain in high_quality:
        if domain in url:
            return 3

    for domain in medium_quality:
        if domain in url:
            return 2

    for domain in low_quality:
        if domain in url:
            return 0

    return 1


# ==================================================
# HELPERS
# ==================================================

def get_hash(text):
    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()


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

            current = current[-overlap:] + " " + sentence + ". "

    if len(current.strip()) > 100:
        chunks.append(current.strip())

    return chunks


# ==================================================
# STORE LIVE RESEARCH DOCUMENTS
# ==================================================

def store_research_docs(search_results):
    stored_count = 0
    seen_urls = set()
    seen_chunk_ids = set()

    for result in search_results:
        url = result.get("url", "")
        title = result.get("title", "Untitled")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        print(f"[RESEARCH FETCH] {title}")
        print(f"[URL] {url}")

        text = fetch_page_text(url)

        if len(text) < 300:
            print("[SKIPPED] Text too short")
            continue

        chunks = chunk_text(text)

        for chunk in chunks:
            chunk = chunk.strip()

            if len(chunk) < 100:
                continue

            chunk_id = get_hash(url + chunk)

            # Avoid duplicates in same run
            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)

            # Avoid duplicates already in ChromaDB
            existing = collection.get(
                ids=[chunk_id]
            )

            if existing and existing["ids"]:
                continue

            embedding = embed_model.encode(
                chunk
            ).tolist()

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[chunk_id],
                metadatas=[
                    {
                        "title": title,
                        "url": url,
                        "type": "live_research",
                        "source_quality": source_score(url)
                    }
                ]
            )

            stored_count += 1

    print(f"[RESEARCH] Stored chunks: {stored_count}")

    return stored_count


# ==================================================
# RETRIEVE RESEARCH CONTEXT
# ==================================================

def retrieve_research_context(question, top_k=8):
    query_embedding = embed_model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    evidence = []

    for doc, meta in zip(docs, metas):
        evidence.append(
            {
                "text": doc,
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "source_quality": meta.get("source_quality", 1)
            }
        )

    # Prefer higher-quality sources in evidence
    evidence = sorted(
        evidence,
        key=lambda item: item.get("source_quality", 1),
        reverse=True
    )

    return evidence


# ==================================================
# MAIN RESEARCH FUNCTION
# ==================================================

def research_answer(question):
    print("[RESEARCH] Question:", question)

    search_query = question + " latest research developments AI 2026"

    search_results = search_web(
        search_query,
        max_results=10
    )

    print("[RESEARCH] Raw search results:", len(search_results))

    # Rank sources by quality
    search_results = sorted(
        search_results,
        key=lambda r: source_score(
            r.get("url", "")
        ),
        reverse=True
    )

    # Remove low-quality sources
    search_results = [
        r for r in search_results
        if source_score(r.get("url", "")) > 0
    ]

    # Keep top 5 after ranking
    search_results = search_results[:5]

    print("[RESEARCH] Filtered search results:", len(search_results))

    if not search_results:
        return {
            "answer": "I could not find reliable sources for that question.",
            "sources": []
        }

    store_research_docs(search_results)

    evidence = retrieve_research_context(
        question,
        top_k=8
    )

    print("[RESEARCH] Evidence found:", len(evidence))

    result = make_research_answer(
        question,
        evidence
    )

    return result