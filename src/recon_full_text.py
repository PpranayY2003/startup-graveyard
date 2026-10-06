import re
import sys
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}
url = "https://www.loot-drop.io/startup/2563-plenty-unlimited"
html = requests.get(url, headers=HEADERS, timeout=30).text
soup = BeautifulSoup(html, "lxml")

out = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    out.append(line)

# 1. The Failure Analysis card: attributes and HTML
h = soup.find("h3", string=lambda s: s and "Failure Analysis" in s)
card = h.find_parent("article") if h else None
log("=== CARD ATTRIBUTES ===")
log(card.attrs if card else "card not found")
log("\n=== CARD HTML (first 2500 chars) ===")
log(str(card)[:2500] if card else "")

# 2. Does text beyond the "..." exist anywhere in the raw HTML?
phrase = "technological impressiveness"
hits = list(re.finditer(phrase, html))
log("\n=== PHRASE OCCURRENCES IN RAW HTML:", len(hits), "===")
for m in hits[:3]:
    start = max(0, m.start() - 200)
    log(f"\n[at {m.start()}] ...{html[start:m.end() + 700]}...")

# 3. Modal-like elements and script tags
log("\n=== MODAL-LIKE ELEMENTS ===")
for el in soup.find_all(class_=re.compile("modal|dialog|overlay|popup|expand", re.I)):
    log(el.name, el.get("id"), el.get("class"), "| text length:", len(el.get_text(strip=True)))

log("\n=== SCRIPT TAGS ===")
for i, s in enumerate(soup.find_all("script")):
    body = s.string or ""
    log(i, dict(s.attrs), "| length:", len(body), "|", body[:150].replace("\n", " "))

with open("data/raw/recon_full_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
