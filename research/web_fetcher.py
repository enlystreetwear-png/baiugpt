import requests
from bs4 import BeautifulSoup

def fetch_page_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        # remove scripts and styles
        for s in soup(["script", "style"]):
            s.extract()
        return " ".join(soup.stripped_strings)
    except Exception as e:
        return ""