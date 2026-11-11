import re
import urllib.parse
from pathlib import Path

import httpx

out = Path(r"c:\Users\DELL\Documents\PROJECTS\ine-hackathon\static\fonts")
out.mkdir(parents=True, exist_ok=True)
sample = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,;:'\"?!()-–—/&"
    "ɓɗƙƴƁƊƘƳịọụṅỊỌỤṄ"
)
css_url = (
    "https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap&text="
    + urllib.parse.quote(sample)
)
css = httpx.get(css_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, follow_redirects=True).text
for weight, url in re.findall(r"font-weight:\s*(\d+);.*?url\(([^)]+)\)", css, re.S):
    name = "NotoSans-Regular.woff2" if weight == "400" else "NotoSans-Bold.woff2"
    data = httpx.get(url, timeout=60, follow_redirects=True).content
    (out / name).write_bytes(data)
    print(name, len(data))
