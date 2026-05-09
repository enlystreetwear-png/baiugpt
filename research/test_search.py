from research.web_search import search_web

query = "latest developments in large language models 2026 AI research"

results = search_web(query, max_results=5)

print("RESULTS:", len(results))

for r in results:
    print("\nTITLE:", r["title"])
    print("URL:", r["url"])
    print("SNIPPET:", r["snippet"])