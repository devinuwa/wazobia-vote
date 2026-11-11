# 07 Track 3 Alignment

Checked against the #AI4Elections Hackathon concept document by Rise Networks. Applications close Thursday 12 November 2026 at 11:59pm WAT.

**Verdict:** a strong fit for Track 3, Inclusive and Multilingual Electoral/Civic Technology. Three gaps should be closed before submitting: languages, a working prototype, and user-testing evidence.

## Fit with Track 3

| Track 3 asks for | What the pack provides | Status |
|---|---|---|
| Accessible voter-information tools | Four accessibility profiles (04) | Covered |
| Nigerian-language electoral and civic information | English, Hausa and Igbo (05) | Partly. Yoruba and Nigerian Pidgin are missing |
| Assistive interfaces for people with disabilities | voice and text_only modes, PWD answering rules | Prompt covered. Needs a real interface and testing |
| Digital literacy | plain mode, icons, low-literacy tone | Covered |
| Barriers to participation | Grounded answers on registration, PVC, polling units | Covered |

## Fit with the mandatory safeguards (section 16)

| Rule | How the pack meets it | Action still needed |
|---|---|---|
| No declaring results, validity or fraud (7.1) | SCOPE bars predictions, validity and fraud claims | None. Tests T04 and T05 |
| Public or authorised data only, NDPA 2023, no voter registers (7.2) | Public sources only. Never asks for voter ID, phone or address | Do not log personal data. Set a short retention limit. Test T23 |
| Transparency and limits, nothing unverified as fact (7.3) | Outcome D and last_verified dates | Show a limits notice in the interface |
| Fairness, accessibility, tested with real users (7.4) | Four profiles | Run the user tests below |
| Cybersecurity (7.5) | Sources treated as data. Injection test T08 | Sandbox only. Keep keys out of code. Never touch live INEC systems |
| Human oversight with named roles (7.6) | needs_human_review flag | Name who reviews flagged replies, who fixes errors, who handles complaints |
| Non-endorsement (7.7 and 18) | "Unofficial, not INEC" in the prompt | Show the same notice in the interface. No INEC logo without written permission |

## Judging criteria

| Criterion | Weight | What to show |
|---|---|---|
| Technical functionality and innovation | 25% | Working demo with grounded answers and JSON validation |
| Electoral relevance and usefulness | 20% | Real voter questions answered from official sources |
| Cybersecurity, privacy, responsible AI | 20% | Privacy rule, injection test, review queue, limits notice |
| Inclusion, accessibility, multilingual | 15% | All four profiles and every supported language, tested with users |
| Scalability and feasibility | 15% | Source pipeline and a clear way to add languages |
| Demonstration and documentation | 5% | This pack and the test results |

The Electoral and Civic Inclusion Award (₦500,000) fits this project directly.

## Gaps and fixes

### 1. Languages

Track 3 says Nigerian languages, and Yoruba and Nigerian Pidgin are widely used. Recommended additions to the master prompt, only after native speakers can review them:

```
LANGUAGE AND VOICE (English, Hausa, Igbo, Yoruba, Nigerian Pidgin)
Yoruba: keep the dot-below letters (ẹ, ọ, ṣ) and tone marks.
Nigerian Pidgin: use simple, widely understood spelling.
If the user writes in a language you do not support, say so in
simple English and offer English, Hausa or Igbo.
If asked whether you are a person, say you are an automated
assistant and not INEC.
```

Until then, keep to English, Hausa and Igbo.

### 2. A working prototype

The competition is Design + Develop only. Mockups and idea-only entries are ineligible, so the prompt alone is not a submission. Minimum build:

1. A low-bandwidth web app that works on a phone.
2. Retrieval over approved public sources, passed as in 03.
3. The model call using 01, with the reply checked against 02.
4. Text-to-speech playing spoken_answer.
5. The four accessibility profiles.
6. A review queue for replies flagged needs_human_review.

### 3. User-testing evidence

Section 7.4 asks for testing with representative users. Plan at least one session with each group and record the results.

1. A blind or low-vision user, using voice mode.
2. A deaf or hard-of-hearing user, using text_only mode.
3. A user with low literacy, using plain mode.
4. Hausa speakers and Igbo speakers, checking wording and spoken output.
5. A first-time voter.

## Eligibility checks before applying

- Every member is of Nigerian origin and at least 18.
- Teams have two to four members, and each member registers individually.
- The application is written in English.
- The project has not already won a grant, award or recognition in another competition.
- Academic teams need a faculty lead, a student or postgraduate researcher, and an approval letter from the head of department.
- Start-ups and organisations need a CAC certificate, at least 60% of members resident in Nigeria, and government ID for all members.

## Questions for the organisers

- The finale is placed in Abuja in one section and Lagos as the convening city in another. Which is it?
- The prize table has typing errors in the second and third place amounts, and some special award descriptions do not match their names. Which figures are final?
- Does using published INEC content in the prototype need written permission?
