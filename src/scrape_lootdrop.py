import json
import random
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://www.loot-drop.io"
HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}
OUT = Path("data/raw/lootdrop_raw.jsonl")
FAILED = Path("data/raw/failed_urls.txt")
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else None  # python scrape_lootdrop.py 5

SECTIONS = {
    "Failure Analysis": "failure_analysis",
    "Market Analysis": "market_analysis",
    "Startup Learnings": "startup_learnings",
    "Market Potential": "market_potential",
    "Difficulty": "difficulty",
    "Scalability": "scalability",
}


def get_startup_urls(session):
    xml = session.get(BASE + "/sitemap.xml", timeout=30).text
    seen, urls = set(), []
    for u in re.findall(r"<loc>(.*?)</loc>", xml):
        if "/startup/" in u and u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def fetch(session, url, tries=3):
    for attempt in range(1, tries + 1):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 200:
                return r.text
            print(f"  status {r.status_code}")
            if r.status_code == 404:
                return None
        except requests.RequestException as e:
            print("  error:", e)
        time.sleep(5 * attempt)  # back off: 5s, 10s, 15s
    return None


def parse_startup(html, url):
    soup = BeautifulSoup(html, "lxml")
    m = re.search(r"/startup/(\d+)-(.+)$", url)

    row = {
        "startup_id": int(m.group(1)) if m else None,
        "slug": m.group(2) if m else None,
        "url": url,
        "name": None,
        "country": None,
        "description": None,
    }

    name = soup.select_one("#startup-name")
    row["name"] = name.get_text(strip=True) if name else None

    country = soup.select_one(".country-tag")
    row["country"] = country.get_text(strip=True).lstrip("\\ ").strip() if country else None

    # stat boxes: SECTOR, PRODUCT TYPE, TOTAL CASH BURNED, FOUNDING YEAR, END YEAR
    for box in soup.select("div.stat-box"):
        label = box.select_one(".stat-label")
        value = box.select_one(".stat-value")
        if label and value:
            key = label.get_text(strip=True).lower().replace(" ", "_")
            row[key] = value.get_text(strip=True)

    # long text sections: full text lives in the data-full-text attribute
    for key in SECTIONS.values():
        row[key] = None
    for card in soup.select("article.grid-card"):
        h3 = card.find("h3")
        title = h3.get_text(strip=True) if h3 else ""
        if title in SECTIONS:
            p = card.select_one("p.card-text")
            text = card.get("data-full-text") or (p.get_text(strip=True) if p else None)
            row[SECTIONS[title]] = text.strip() if text else None

    # intro paragraph (best effort): first long paragraph outside the cards
    for p in soup.find_all("p"):
        if p.find_parent("article") is None:
            t = p.get_text(" ", strip=True)
            if len(t) > 100:
                row["description"] = t
                break

    return row


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)

    urls = get_startup_urls(session)
    print("startup pages in sitemap:", len(urls))

    done = set()
    if OUT.exists():
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["url"])
    print("already scraped:", len(done))

    todo = [u for u in urls if u not in done]
    if LIMIT:
        todo = todo[:LIMIT]
    print("to scrape now:", len(todo), "\n")

    with open(OUT, "a", encoding="utf-8") as out:
        for i, url in enumerate(todo, 1):
            try:
                html = fetch(session, url)
                if html is None:
                    raise ValueError("no html")
                row = parse_startup(html, url)
                row["scraped_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()
                print(f"[{i}/{len(todo)}] {row['name']} | {row.get('sector')} | {row.get('total_cash_burned')}")
            except Exception as e:
                print(f"[{i}/{len(todo)}] FAILED {url} ({e})")
                with open(FAILED, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
            time.sleep(random.uniform(1, 2))

    print("\ndone.")


if __name__ == "__main__":
    main()
