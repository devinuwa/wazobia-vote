# Knowledge Files (the only allowed sources)

Give each file a header with `id`, `title`, `url` and `last_verified`, for example `src-001`.

## Header template

Put this at the top of every uploaded knowledge file:

```
id: src-001
title: [Human-readable name of the document or page]
url: [Official page the text came from]
last_verified: YYYY-MM-DD
---
[Passage exactly as published. Do not paraphrase or merge.]
```

## Files to collect

- [x] **The current Electoral Act in force.** Gazette copy of the Electoral Act, 2026 (Official Gazette No. 40, Lagos, 2 March 2026). The Act states that it repeals the Electoral Act No. 13, 2022. Saved as `knowledge/src-001.txt`.
- [x] **INEC public guidelines:**
  - [x] Voter registration. Registration rules are taken from the Electoral Act, 2026 (`knowledge/src-001.txt`). The older Continuous Voter Registration Guide was moved to `source-originals/outdated/src-002.txt` because its own text tells officials to read the Electoral Act 2006. The separate 2006 guidelines were not added.
  - [ ] PVC collection. No 2026–2027 collection procedure was found. See the collection notes.
  - [x] Regulations and Guidelines for the Conduct of Elections, 2026. Saved as `knowledge/src-003.txt` by OCR, with `ocr: true` and a page marker on every page. `last_verified` is empty.
  - [ ] INEC's framework for persons with disabilities. No framework file was found on the current INEC site.
- [ ] **ACE Electoral Knowledge Network pages** on registration, voting operations and election technology. The site returned errors on 9 November 2026, so these pages were not saved.
- [x] **International IDEA publications** on technology in elections. Six publications were saved as `knowledge/src-009.txt` through `knowledge/src-014.txt`.

## Tracking table

| id | title | source | url | last_verified |
|---|---|---|---|---|
| src-001 | Electoral Act, 2026 | National Assembly gazette | https://nass.gov.ng/documents/download/11248 | |
| src-003 | Regulations and Guidelines for the Conduct of Elections, 2026 (ocr: true) | INEC | https://inecnigeria.org/documents/guidelines/REGULATIONS-AND-GUIDELINES-FOR-2026.pdf | |
| src-004 | PLACEHOLDER — separate election-day pamphlet (excluded from retrieval) | INEC | | |
| src-005 | PLACEHOLDER — Framework for persons with disabilities (excluded from retrieval) | INEC | | |
| src-006 | PLACEHOLDER — Registration page (excluded from retrieval) | ACE | https://aceproject.org/ace-en/topics/vr/onePage | |
| src-007 | PLACEHOLDER — Voting operations page (excluded from retrieval) | ACE | https://aceproject.org/ace-en/topics/vo/onePage | |
| src-008 | PLACEHOLDER — Election technology page (excluded from retrieval) | ACE | https://aceproject.org/ace-en/topics/et/onePage | |
| src-009 | Introducing Electronic Voting: Essential Considerations | International IDEA | https://www.idea.int/sites/default/files/publications/introducing-electronic-voting.pdf | |
| src-010 | Cybersecurity in Elections: Models of Interagency Collaboration | International IDEA | https://www.idea.int/sites/default/files/publications/cybersecurity-in-elections-models-of-interagency-collaboration.pdf | |
| src-011 | Certification of ICTs in Elections | International IDEA | https://www.idea.int/sites/default/files/publications/certification-of-icts-in-elections.pdf | |
| src-012 | Introducing Biometric Technology in Elections | International IDEA | https://www.idea.int/sites/default/files/publications/introducing-biometric-technology-in-elections-reissue.pdf | |
| src-013 | The Use of Open Source Technology in Elections | International IDEA | https://www.idea.int/sites/default/files/publications/the-use-of-open-source-technology-in-elections.pdf | |
| src-014 | Open Data in Electoral Administration | International IDEA | https://www.idea.int/sites/default/files/publications/open-data-in-electoral-administration.pdf | |

## Collection notes (9 November 2026)

These files were not saved. Nothing was written in from memory.

- **PVC collection.** `inecnigeria.org` has a "List of PVC Collection Centres for Ward Level Collection" for 6–15 January 2023, and an Osun State table of collected and uncollected PVCs. Neither document is a collection procedure, so neither was saved as src-003.
- **Election-day procedures.** `https://inecnigeria.org/documents/guidelines/REGULATIONS-AND-GUIDELINES-FOR-2026.pdf` downloaded (41 pages) and every page had an empty text layer. It was not retyped. The voter-education PDF "2023 General Election Voting Procedures" does have text, and it prints the February and March 2023 election dates, so it was not saved as the current procedure.
- **Persons with disabilities.** The current site's document list has no "Framework on Access and Participation of Persons with Disabilities" file. The old host `wp1.inecnigeria.org` does not resolve from this machine.
- **Current CVR exercise PDF.** `https://wp1.inecnigeria.org/wp-content/uploads/CONTINUOUS-VOTER-REGISTRATION-CVR-2025-2026_w-new-offices-4.pdf` could not be downloaded because that host does not resolve.
- **ACE.** `https://aceproject.org/` returned a site error, and the registration, voting-operations, and election-technology topic pages returned 404. A later retry the same evening: the homepage responded, and `https://aceproject.org/ace-en/topics/vr/onePage` returned 404, `https://aceproject.org/ace-en/topics/vo/onePage` returned 503, and `https://aceproject.org/ace-en/topics/et/onePage` returned 503. No mirror was used. Placeholder files `knowledge/src-006.txt` through `knowledge/src-008.txt` remain and are left out of retrieval.

## Collection notes (later on 9 November 2026)

- **src-002.** Moved to `source-originals/outdated/src-002.txt`. It is not retrieved. The 2006 registration guidelines were not added.
- **src-003.** `source-originals/regulations-and-guidelines-2026.pdf` was read with OCR, one page at a time, into `knowledge/src-003.txt`. The wording was not corrected. Proofreading list: `ocr-check.md`.
- **2027 timetable and notice of election.** No downloadable timetable or notice file was found in the current INEC document list. These addresses could not be downloaded: `https://wp1.inecnigeria.org/press-conference-by-the-inec-chairman-professor-joash-o-amupitan-san-on-friday-13th-february-2026/` (host does not resolve), `https://inecnigeria.org/documents/2027` (404), `https://inecnigeria.org/documents/press/2027` (404). The calendar page `https://inecnigeria.org/elections/calendar` is a web page, not a file, so its dates were not copied into `/knowledge`.
- **PVC collection, 2026–2027.** No collection-procedure file for that period was in the current document list. Older centre lists and state statistics were not saved.
- **Persons with disabilities.** The current document list still has no framework PDF. `https://wp1.inecnigeria.org/` does not resolve, so the older framework write-ups on that host could not be downloaded.
- **Another regulations file on the same site.** `https://inecnigeria.org/documents/parties/Regulations-and-Guidelines-2026_UPDATED.pdf` responded as a PDF. It was not substituted for the file that was OCR'd.

## Rules

- Use ACE and IDEA only for general electoral concepts and technology in elections.
- Use the Electoral Act and INEC guidelines for Nigerian deadlines, eligibility, polling units and legal rights.
- Re-check `last_verified` regularly. Flag any file older than 30 days for deadlines and polling units, and 90 days for everything else.
