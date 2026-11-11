import re
from pathlib import Path

path = Path("knowledge/src-001.txt")
lines = path.read_text(encoding="utf-8").splitlines()
header = re.compile(r"A\s+(\d+)")
section = re.compile(r"^(\d{1,3})\.(?:\s*—|\s+\S)")
page = ""
wanted = {
    "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "47", "48", "49", "50", "54",
}
found = []
for index, line in enumerate(lines, start=1):
    match = header.search(line)
    if match and ("Electoral Act" in line or "2026" in line):
        page = match.group(1)
    start = section.match(line)
    if start and start.group(1) in wanted and index > 240:
        found.append((start.group(1), page, index, line[:110]))

seen = set()
for number, page, index, text in found:
    if number in seen:
        continue
    seen.add(number)
    print(f"section {number}\tgazette page {page}\tline {index}\t{text}")
