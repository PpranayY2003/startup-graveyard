import json
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}
url = "https://www.loot-drop.io/startup/2563-plenty-unlimited"

html = requests.get(url, headers=HEADERS, timeout=30).text
soup = BeautifulSoup(html, "lxml")

# 1. ld+json blocks
print("=== LD+JSON ===")
for s in soup.find_all("script", type="application/ld+json"):
    try:
        print(json.dumps(json.loads(s.string), indent=2)[:3000])
    except Exception as e:
        print("could not parse:", e, (s.string or "")[:500])
    print("-----")

# 2. headings (shows the page sections)
print("\n=== HEADINGS ===")
for h in soup.find_all(["h1", "h2", "h3", "h4"]):
    print(h.name, "|", h.get_text(" ", strip=True)[:100])

# 3. short label-like text (e.g. "Founded", "Raised", "Shut down")
print("\n=== SHORT LABELS (likely fields) ===")
seen = set()
for tag in soup.find_all(["span", "div", "p", "dt", "dd", "li", "td", "th"]):
    t = tag.get_text(" ", strip=True)
    if 2 < len(t) < 60 and t not in seen:
        seen.add(t)
        print(" ", t)
