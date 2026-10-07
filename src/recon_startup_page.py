import re
import requests

BASE = "https://www.loot-drop.io"
HEADERS = {"User-Agent": "startup-graveyard-portfolio-project (personal, non-commercial)"}

sitemap = requests.get(BASE + "/sitemap.xml", headers=HEADERS, timeout=30).text
urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
startup_urls = [u for u in urls if "/startup/" in u]
print("startup pages:", len(startup_urls))

url = startup_urls[0]
print("testing:", url)
r = requests.get(url, headers=HEADERS, timeout=30)
html = r.text
print("status:", r.status_code, "| size:", len(html))

with open("data/raw/sample_startup.html", "w", encoding="utf-8") as f:
    f.write(html)

print("title:", re.findall(r"<title>(.*?)</title>", html, flags=re.S))
print("has __NEXT_DATA__:", "__NEXT_DATA__" in html)
print("has ld+json:", "application/ld+json" in html)
print("script tags:", len(re.findall(r"<script", html)))

text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text).strip()
print("\nvisible text preview:\n", text[:1200])
