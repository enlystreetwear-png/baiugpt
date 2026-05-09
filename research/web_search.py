# research/web_search.py

from ddgs import DDGS


def search_web(query, max_results=5):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", "") or r.get("url", ""),
                    "snippet": r.get("body", "")
                })

    except Exception as e:
        print("[SEARCH ERROR]", e)

    print(f"[SEARCH] Found {len(results)} results")

    return results