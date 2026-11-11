# 03 Sources Format

The assistant answers only from the `<sources>` block. Your retrieval layer builds it for each question.

## Block layout

```
<sources>
  <source id="src-001" title="Example title"
          url="https://example.org/page"
          last_verified="2026-01-15">
    Example text only. Replace with the real published text.
  </source>
  <source id="src-002" ...>...</source>
</sources>

<question>The user's words, unchanged.</question>
```

The values above are placeholders. They are not real INEC content.

## Fields

| Field | Rule |
|---|---|
| id | Unique and stable. This is what the model cites |
| title | Human-readable name of the page or document |
| url | The official page the text came from |
| last_verified | Date a person last checked the text against the original, as YYYY-MM-DD |
| body | The passage itself, plain text |

## Rules for the retrieval layer

- Include only text from INEC's official channels and other sources you have approved. Keep a separate section of PWD (persons with disabilities) material so disability questions are answered from it.
- Send the passage as written. Do not paraphrase or merge passages, because the model must copy dates, numbers, times and place names exactly.
- Escape any angle brackets inside a passage so it cannot close the block early.
- Pass your own staleness limit with each request, for example the number of days after which a source counts as old.
- When nothing relevant is found, send an empty sources block. The model should then answer with outcome B and point to INEC's official channels.

## Why sources are treated as data

A passage may contain text such as "ignore your rules". The prompt tells the model to ignore any instruction inside sources. Test this in 06 (T08) after every prompt or retrieval change.
