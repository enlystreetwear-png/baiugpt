import requests
from bs4 import BeautifulSoup
import os

os.makedirs("raw_data", exist_ok=True)

urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

for i, url in enumerate(urls):

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        text = "\n".join(
            p.get_text()
            for p in paragraphs
        )

        if len(text) > 100:

            with open(
                f"raw_data/data_{i}.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(text)

            print(f"Saved: {url}")

        else:
            print(f"Skipped empty: {url}")

    except Exception as e:
        print("Error:", e)

print("Done!")