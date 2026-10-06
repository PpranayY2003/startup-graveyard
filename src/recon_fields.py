import sys
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}
url = "https://www.loot-drop.io/startup/2563-plenty-unlimited"
soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=30).text, "lxml")

print("=== H1 HTML ===")
print(str(soup.find("h1"))[:500])

print("\n=== FIELD LABELS (SECTOR, TOTAL CASH BURNED, ...) ===")
for label in ["SECTOR", "PRODUCT TYPE", "TOTAL CASH BURNED", "FOUNDING YEAR", "END YEAR"]:
    el = soup.find(string=lambda s: s and s.strip() == label)
    print(f"\n[{label}] parent HTML:")
    print(str(el.parent.parent)[:600] if el else "NOT FOUND")

print("\n=== SECTIONS (what follows each heading) ===")
for label in ["Failure Analysis", "Market Analysis", "Startup Learnings",
              "Market Potential", "Difficulty", "Scalability"]:
    h = soup.find("h3", string=lambda s: s and label in s)
    print(f"\n[{label}]")
    if not h:
        print("  NOT FOUND")
        continue
    for el in h.find_all_next(limit=3):
        print("  ", el.name, el.get("class"), "|", el.get_text(" ", strip=True)[:300])
