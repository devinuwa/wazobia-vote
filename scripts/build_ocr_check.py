import re
from pathlib import Path

text = Path("knowledge/src-003.txt").read_text(encoding="utf-8")
pages = re.split(r"\n--- page (\d+) ---\n", text)
# pages[0] is the header, then number, body, number, body...
chunks = []
for index in range(1, len(pages), 2):
    chunks.append((int(pages[index]), pages[index + 1]))

months = (
    "January|February|March|April|May|June|July|August|September|"
    "October|November|December"
)
date_patterns = [
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{months})\s+\d{{4}}\b",
    rf"\b(?:{months})\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
]
time_patterns = [
    r"\b\d{1,2}[.:]\d{2}(?::\d{2})?\s*(?:a\.?\s?m\.?|p\.?\s?m\.?)?",
    r"\b\d{1,2}\s*(?:a\.m\.|p\.m\.)\b",
]
number_pattern = r"\b\d+(?:[.,]\d+)*\b"
states = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
    "Abuja", "Federal Capital Territory", "FCT", "Nigeria",
]

def find_all(patterns, body):
    found = []
    for pattern in patterns:
        for match in re.finditer(pattern, body, re.I):
            found.append((match.start(), match.group(0)))
    found.sort()
    return found

lines = [
    "# OCR check for src-003",
    "",
    "The text in `knowledge/src-003.txt` is the Windows OCR reading of `source-originals/regulations-and-guidelines-2026.pdf`. Nothing in that file was corrected. Compare each item below with the same page of the PDF.",
    "",
    f"Pages: {len(chunks)}",
    "",
]
for number, body in chunks:
    lines.append(f"## Page {number}")
    lines.append("")
    dates = find_all(date_patterns, body)
    times = find_all(time_patterns, body)
    numbers = [match.group(0) for match in re.finditer(number_pattern, body)]
    places = []
    for name in states:
        for match in re.finditer(rf"\b{re.escape(name)}\b", body, re.I):
            places.append(match.group(0))
    for match in re.finditer(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s+State\b", body):
        places.append(match.group(0))
    lines.append("Dates: " + (", ".join(item for _, item in dates) if dates else "none found"))
    lines.append("")
    lines.append("Times: " + (", ".join(item for _, item in times) if times else "none found"))
    lines.append("")
    lines.append("Numbers: " + (", ".join(numbers) if numbers else "none found"))
    lines.append("")
    lines.append("Place names: " + (", ".join(places) if places else "none found"))
    lines.append("")

Path("ocr-check.md").write_text("\n".join(lines), encoding="utf-8")
print("pages", len(chunks), "lines", len(lines))
