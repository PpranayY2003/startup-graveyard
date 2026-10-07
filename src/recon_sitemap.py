import re
from collections import Counter
import requests

URL = "https://www.loot-drop.io/sitemap.xml"
HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}

r = requests.get(URL, headers=HEADERS, timeout=30)
print("status:", r.status_code, "| size:", len(r.text))

urls = re.findall(r"<loc>(.*?)</loc>", r.text)
print("total urls:", len(urls))

def pattern(u):
    path = u.replace("https://www.loot-drop.io", "")
    path = re.sub(r"\d+", "{n}", path)
    return path.split("?")[0] or "/"

counts = Counter(pattern(u) for u in urls)
for p, n in counts.most_common(25):
    print(f"{n:>5}  {p}")

print("\nsample urls:")
for u in urls[:15]:
    print(" ", u)
print("\nany startup.html urls:", any("startup.html" in u for u in urls))
