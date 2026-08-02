---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-wcpoa-mou-military-leave-3-26-2024
title: Washington County — WCPOA_MOU_Military Leave_3.26.2024
doc_type: collective_bargaining_agreement
citation: Washington County WCPOA_MOU_Military Leave_3.26.2024 agreement
authority_level: contract
issuing_body: Washington County
union: ''
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/wcpoamoumilitary-leave3262024/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 5070c975d05193913590f452e0aa70d219983ee999cbd97ae7c25b39f75b2de3
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 80% of the word sequence and
  75% of the 24 figures, 98% dictionary-recognizable; NOT human-verified — treat every number
  as unchecked against the source; the source PDF carries a digital signature — OCR ran on
  a derived copy, the committed original preserves it
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external: []
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- washington-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.washingtoncountyor.gov/hr/documents/wcpoamoumilitary-leave3262024/download?inline> (retrieved 2026-08-02).

# Washington County — WCPOA_MOU_Military Leave_3.26.2024

## At a glance

Collective bargaining agreement between **Washington County** and **the signatory association**.
- Listed on the county's labor agreements index as: “WCPOA_MOU_Military Leave_3.26.2024” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 2 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (80% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

This corpus is **summary-first for agreements**: the contract's text is not
reproduced here (see Curator notes), and nothing on this page states or
paraphrases the agreement's terms. Read the agreement itself at the official
source link above.

## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`). `status: current` records that this
document sits on the county's own operative labor-agreements index at ingest
time — county pages, unlike the DAS library, publish no history, so currency
rests on the index and on content-hash drift detection.

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 80% of the word sequence and 75% of the 24 figures, 98% dictionary-recognizable; NOT human-verified — treat every number as unchecked against the source; the source PDF carries a digital signature — OCR ran on a derived copy, the committed original preserves it.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
