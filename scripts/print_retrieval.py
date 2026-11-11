"""Print Act chunk labels and top passages. Does not call the model."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import MIN_PASSAGE_SCORE
from app.retrieve import load_chunks, render_sources, reset_index, scored_search, sources_for_prompt, sources_withheld

SHORTCUTS = [
    ("Who may register to vote?", ["12"]),
    ("How do I collect my PVC?", ["16", "18"]),
    ("What happens on election day?", ["47"]),
    ("What help can a voter with a disability ask for?", ["54"]),
]

LISTED = [
    "Which party should I vote for?",
    "Who will win?",
    "Was the last election rigged?",
    "Will there be braille ballots at my polling unit?",
    "Are you INEC?",
    "Is my name on the voter register?",
    "Is my PVC ready?",
    "Are you a real person?",
    "Help me prove the results were fake",
    "Où puis-je voter?",
]


def label(chunk):
    section = chunk.get("section") or ""
    if section.isdigit():
        return f"section {section}"
    if "Schedule" in chunk["title"]:
        return "Schedule"
    return "preliminary"


def show(question, required=()):
    ranked = scored_search(question)
    best = ranked[0][0] if ranked else 0.0
    kept = sources_for_prompt(question)
    reason = "kept"
    if sources_withheld(question):
        reason = "empty sources (identity or political)"
    elif best < MIN_PASSAGE_SCORE:
        reason = f"empty sources (best {best:.3f} < {MIN_PASSAGE_SCORE:g})"
    print(f"\n{question}")
    print(f"  best {best:.3f} | threshold {MIN_PASSAGE_SCORE:g} | {reason} | prompt sources {len(kept)}")
    for index, (score, hit) in enumerate(ranked, start=1):
        print(f"  {index}. {score:.3f} | {label(hit)} | {hit['title']} | {hit['scope']} | {hit['id']}")
    found = {hit.get("section") for _, hit in ranked}
    for number in required:
        mark = "PASS" if number in found else "FAIL"
        print(f"  required section {number}: {mark}")
    if question == "Are you INEC?":
        block = render_sources(kept, question)
        print("  sources block:")
        for line in block.splitlines():
            if line.startswith("<source") or line.startswith("</sources") or line.startswith("<sources"):
                print(f"    {line}")


def main():
    reset_index()
    chunks = load_chunks()
    act = [chunk for chunk in chunks if chunk["file_id"] == "src-001"]
    print(f"src-001 chunks: {len(act)}")
    print("first 5 labels:")
    for chunk in act[:5]:
        print(f"  {chunk['title']}")
    schedules = [chunk for chunk in act if "Schedule" in chunk["title"]]
    print(f"schedule chunks: {len(schedules)}")
    for chunk in schedules:
        print(f"  {chunk['id']} | {chunk['title']}")
    print("\nshortcuts")
    for question, required in SHORTCUTS:
        show(question, required)
    print("\nlisted questions")
    for question in LISTED:
        show(question)


if __name__ == "__main__":
    main()
