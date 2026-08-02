---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-afscme-cc-mou-trimet-insurance-pay-period-11-18-2025-pdf
title: Washington County — AFSCME CC MOU_TriMet Insurance Pay Period 11-18-2025.pdf
doc_type: collective_bargaining_agreement
citation: 2024-2027 Washington County AFSCME agreement
authority_level: contract
issuing_body: Washington County
union: AFSCME
term: 2024-2027
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/afscme-cc-moutrimet-insurance-pay-period-11-18-2025pdf/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 5cff0da85bbc4a7930bedb816a93bb72ac20f41668c9ab209ac62f24548eea98
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 81% of the word sequence and
  80% of the 127 figures, 94% dictionary-recognizable; 3 heading/letterhead token(s) lost
  their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified
  — treat every number as unchecked against the source; the source PDF carries a digital signature
  — OCR ran on a derived copy, the committed original preserves it
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
> source: <https://www.washingtoncountyor.gov/hr/documents/afscme-cc-moutrimet-insurance-pay-period-11-18-2025pdf/download?inline> (retrieved 2026-08-02).

# Washington County — AFSCME CC MOU_TriMet Insurance Pay Period 11-18-2025.pdf

## At a glance

Collective bargaining agreement between **Washington County** and **AFSCME** — **2024-2027** term.
- Listed on the county's labor agreements index as: “AFSCME CC MOU_TriMet Insurance Pay Period 11-18-2025.pdf” (index archived in `_meta/discovery/`)
- Source document: 4 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (81% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 81% of the word sequence and 80% of the 127 figures, 94% dictionary-recognizable; 3 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source; the source PDF carries a digital signature — OCR ran on a derived copy, the committed original preserves it.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
