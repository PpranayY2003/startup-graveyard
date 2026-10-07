import re
import requests

BASE = "https://www.loot-drop.io"
HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}

# 1. robots.txt
r = requests.get(BASE + "/robots.txt", headers=HEADERS, timeout=30)
print("robots.txt status:", r.status_code)
print(r.text[:2000])

# 2. look for scraping/terms language on a few pages
keywords = ["scrap", "terms", "api", "license", "attribution", "commercial", "copyright", "download", "export"]
for path in ["/faq", "/story", "/database-view"]:
    page = requests.get(BASE + path, headers=HEADERS, timeout=30)
    text = re.sub(r"<[^>]+>", " ", page.text)
    print(f"\n--- {path} (status {page.status_code}) ---")
    for k in keywords:
        for m in re.finditer(k, text, flags=re.I):
            start = max(0, m.start() - 80)
            print(f"[{k}] ...{text[start:m.end()+80].strip()}...")
            break
