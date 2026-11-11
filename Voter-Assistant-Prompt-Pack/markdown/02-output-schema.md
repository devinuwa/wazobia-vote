# 02 Output Schema

The model returns one JSON object and nothing else. No prose before or after, no code fence.

## Fields

| Field | Type | Rule |
|---|---|---|
| outcome | string | Exactly one of "A", "B", "C" or "D" |
| language | string | Language of the reply. Recommended codes: en, ha, ig |
| language_confidence | string | high, medium or low |
| spoken_answer | string | Read aloud. Short sentences, no markdown, no URLs, numbers and dates in words, ends with one next step |
| display_answer | string | Shown on screen. Shaped by the accessibility profile |
| steps | array | Items of text and icon. Empty array when no steps apply. icon is an id from {icon_ids} or empty |
| citations | array | Items of id, title, url, last_verified, copied from the sources used |
| confidence | string | high, medium or low |
| needs_human_review | boolean | True for every outcome D, and whenever a term is unsure |
| reason_for_review | string | Empty unless needs_human_review is true |

## What each outcome implies

| Outcome | Meaning | Citations | Review flag |
|---|---|---|---|
| A | Sources clearly answer | Required | False |
| B | Sources cover part | Required for the supported part | Usually false |
| C | Out of scope or political | May be empty | False |
| D | High-stakes and sources thin, conflicting or old | Cite what exists | True |

In outcome D, display_answer and spoken_answer must say the answer is "not yet verified".

## Validation schema (JSON Schema 2020-12)

```
{
  "type": "object",
  "additionalProperties": false,
  "required": ["outcome", "language", "language_confidence",
    "spoken_answer", "display_answer", "steps", "citations",
    "confidence", "needs_human_review", "reason_for_review"],
  "properties": {
    "outcome": {"enum": ["A", "B", "C", "D"]},
    "language": {"type": "string"},
    "language_confidence": {"enum": ["high", "medium", "low"]},
    "spoken_answer": {"type": "string", "minLength": 1},
    "display_answer": {"type": "string", "minLength": 1},
    "steps": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["text", "icon"],
      "properties": {"text": {"type": "string"},
                     "icon": {"type": "string"}}}},
    "citations": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "title", "url", "last_verified"],
      "properties": {"id": {"type": "string"},
                     "title": {"type": "string"},
                     "url": {"type": "string"},
                     "last_verified": {"type": "string"}}}},
    "confidence": {"enum": ["high", "medium", "low"]},
    "needs_human_review": {"type": "boolean"},
    "reason_for_review": {"type": "string"}
  },
  "allOf": [
    {"if": {"properties": {"outcome": {"const": "D"}}},
     "then": {"properties": {"needs_human_review": {"const": true}}}}
  ]
}
```

## Checks the schema cannot do

- Every citations id exists in the supplied sources, and title, url and last_verified match them.
- spoken_answer contains no URL, no markdown symbols and no digits.
- In text_only mode, steps has at most five items.
- In plain mode, every icon is in {icon_ids} or empty.
- No voter ID, phone number or address appears anywhere in the reply.
