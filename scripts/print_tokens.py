"""Print request and sources token sizes. Does not call the model."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import SOURCE_TOKEN_CAP
from app.prompt import system_message
from app.retrieve import render_sources, sources_for_prompt
from app.tokens import count_tokens, fit_passages

QUESTIONS = [
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


def main():
    system = system_message("voice")
    print(f"system prompt tokens: {count_tokens(system)}")
    print(f"sources cap: {SOURCE_TOKEN_CAP}")
    print("count: one token per short word or mark, one per four letters of a longer word")
    for question in QUESTIONS:
        raw = sources_for_prompt(question)
        fitted = fit_passages(raw, question, render_sources)
        before = count_tokens(render_sources(raw, question))
        after = count_tokens(render_sources(fitted, question))
        request = count_tokens(system) + after
        print(
            f"{question} | passages {len(raw)}->{len(fitted)} | "
            f"sources {before}->{after} | request {request}"
        )


if __name__ == "__main__":
    main()
