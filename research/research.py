from ddgs import DDGS
from research.web_fetcher import fetch_page_text
from research.reasoner import make_research_answer

CREATOR_KEYWORDS = [
    "youtube",
    "creator",
    "content",
    "video",
    "shorts",
    "gaming",
    "channel",
    "audience",
    "retention",
    "thumbnail",
    "title",
    "seo",
]

def search_web(query, max_results=5):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", "")
            })
    return results

def research_answer(question, niche=None, max_results=5):
    topic = niche or "YouTube"
    search_query = (
        f"YouTube creator growth strategy {topic} niche "
        f"audience retention thumbnails titles content ideas {question}"
    )

    search_results = search_web(search_query, max_results=max_results)
    evidence_texts = []

    for res in search_results:
        try:
            text = fetch_page_text(res["url"])
            evidence_blob = f"{res.get('title', '')} {res.get('url', '')} {text[:1500]}".lower()
            is_relevant = any(keyword in evidence_blob for keyword in CREATOR_KEYWORDS)

            if len(text) > 200 and is_relevant:
                evidence_texts.append({"text": text, "title": res["title"], "url": res["url"]})
        except Exception:
            continue

    # Pass question + evidence to reasoning
    answer = make_research_answer(question, evidence_texts, niche=niche)
    return answer
