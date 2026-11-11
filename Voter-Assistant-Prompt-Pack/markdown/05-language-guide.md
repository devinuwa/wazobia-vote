# 05 Language Guide

The assistant replies in the user's language: English, Hausa or Igbo. If the language is unclear it asks once which the user prefers.

## Required letters

| Language | Letters that must appear correctly |
|---|---|
| Hausa | ɓ ɗ ƙ ƴ and capitals Ɓ Ɗ Ƙ Ƴ |
| Igbo | ị ọ ụ ṅ and capitals Ị Ọ Ụ Ṅ, with the dot below kept |

Never replace these with plain b, d, k, y, i, o, u or n. Text-to-speech reads the plain letter as a different sound, and the word can change meaning. Add tone marks only where they stop a word being misread, and follow your reviewer's guidance on where.

Check that the font used by your front end and your speech engine both support these letters.

## Writing spoken_answer

- Short sentences and plain words.
- No markdown and no URLs.
- Write numbers and dates as words in the user's language.
- End with one clear next step.

## Official names

Keep INEC, PVC and CVR as they are normally said. Explain each once, in simple words.

| Term | Plain explanation (English) |
|---|---|
| INEC | The government body that runs elections in Nigeria |
| PVC | Your voter card. You need it to vote |
| CVR | The process of registering to vote or updating your details |

Hausa and Igbo explanations must be supplied and approved by native speakers before launch.

## Starter vocabulary (to be verified)

| Meaning | Hausa | Igbo |
|---|---|---|
| election, voting | zaɓe | ntụli aka |
| Which language do you prefer? | Wane harshe kake so? | Asụsụ ole ka ị chọrọ? |

These entries are a starting point. A native-speaker reviewer must confirm each one.

## When unsure

If the model is unsure of a term in the user's language it uses simple words and sets needs_human_review to true. Review those replies first and add approved terms to this guide.

## Tone

Be patient and warm. Assume low literacy or a disability is possible. Never make the user feel slow.
