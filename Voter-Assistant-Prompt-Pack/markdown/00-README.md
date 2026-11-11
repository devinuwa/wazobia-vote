# Read Me

An unofficial voter-information assistant for Nigerian elections. It answers from supplied sources only, in English, Hausa or Igbo, in a form the user can actually use. It is not INEC and never speaks for INEC. The master prompt keeps the wording as supplied; only line breaks and layout were restored.

## Files in this pack

| File | Purpose |
|---|---|
| 01-master-prompt | The system prompt. Fill three placeholders, then send |
| 02-output-schema | The JSON the model returns, with a validation schema |
| 03-sources-format | How retrieved sources are passed in as data |
| 04-accessibility-profiles | What each profile changes in the reply |
| 05-language-guide | Orthography, spoken-answer rules, glossary starter |
| 06-test-cases | Acceptance tests for every outcome and rule |
| 07-track3-alignment | Check against the AI4Elections concept document, gaps and next steps |

## Runtime assembly

1. System message: the text of 01-master-prompt with `{app_name}`, `{accessibility_profile}` and `{icon_ids}` filled in.
2. User message: a `<sources>` block (see 03), then the user's question.
3. Response: one JSON object only (see 02). Validate it before showing anything to the user.

| Placeholder | Filled with |
|---|---|
| `{app_name}` | The product name shown to users |
| `{accessibility_profile}` | One of voice, large_text, text_only, plain, or empty |
| `{icon_ids}` | The list of icon ids your front end can render (used by plain mode) |

## Open decisions for the deployer

1. **Language-unclear turn.** The prompt says to ask once which language the user prefers, but every reply must carry an outcome A to D. Recommended: use outcome B, set language_confidence to low, and put the question in all three languages in spoken_answer and display_answer.
2. **What counts as old.** The prompt says to flag an old last_verified date but sets no limit. Set one in code and pass it with each source, for example a number of days, shorter for deadlines and polling units.
3. **Server-side checks.** Reject any reply where a cited id is not in the supplied sources, where spoken_answer contains a URL or markdown, or where outcome is D but needs_human_review is false.
4. **Native review.** Have Hausa and Igbo speakers review every reply type, and the glossary in 05, before launch.
