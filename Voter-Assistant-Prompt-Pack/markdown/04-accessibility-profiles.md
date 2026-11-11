# 04 Accessibility Profiles

One profile is supplied per request. It changes how the reply is written, never what is true.

## Profiles

| Profile | Who it serves | What changes |
|---|---|---|
| voice | A user who is blind or cannot read | spoken_answer is complete on its own. Nothing visual is mentioned. Steps come in order, one at a time |
| text_only | A user who is deaf or hard of hearing | display_answer carries everything. Very short sentences, common words, at most five steps. No idioms, no unexplained abbreviations |
| large_text | A user who enlarges the screen | display_answer is short and structured so it stays readable when enlarged |
| plain | A user who reads with difficulty | One idea per step, simple words, each step has an icon id from {icon_ids} or an empty icon |
| none given | Unknown | Write for the widest audience: simple words, short sentences, a complete spoken_answer |

## Never say in voice mode

Phrases that point at the screen, such as "see below", "click the button" or "as shown". Say what to do instead.

## Icon ids

The front end owns the icon set. Pass its ids in {icon_ids}. An example set to replace with your own:

`id-card`, `location-pin`, `calendar`, `clock`, `phone`, `person-assist`, `ballot-box`, `check`, `warning`, `question`

The model may only use ids from the list you send, or leave the icon empty.

## Disability questions

Answer from the PWD sources. Cover three things:

1. What INEC provides.
2. What the voter may ask for, for example priority voting, or help from a person of their choice.
3. Who to ask.

Never promise that a specific aid will be at a particular polling unit. Use wording such as "you can ask for" and "INEC says it provides", never "there will be".
