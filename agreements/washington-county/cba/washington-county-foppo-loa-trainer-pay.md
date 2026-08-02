---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-foppo-loa-trainer-pay
title: Washington County — FOPPO LOA_Trainer Pay
doc_type: collective_bargaining_agreement
citation: Washington County FOPPO agreement
authority_level: contract
issuing_body: Washington County
union: FOPPO
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/foppo-loatrainer-pay/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 33c75017066b96f10c9d45c45e982b083e2f918cae834946d2f098ebc69a368c
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: 'no text layer in the source PDF; text recovered by OCR. Two independent
  engines (docTR (DBNet + CRNN) + paddleocr PP-OCRv6) agree on 97% of the word sequence and
  100% of the 15 figures, 97% dictionary-recognizable; different-pair recovery: tesseract
  produced no usable text on this scan; NOT human-verified — treat every number as unchecked
  against the source'
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
> source: <https://www.washingtoncountyor.gov/hr/documents/foppo-loatrainer-pay/download?inline> (retrieved 2026-08-02).

# Washington County — FOPPO LOA_Trainer Pay

## At a glance

Collective bargaining agreement between **Washington County** and **FOPPO**.
- Listed on the county's labor agreements index as: “FOPPO LOA_Trainer Pay” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 1 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (97% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (docTR (DBNet + CRNN) + paddleocr PP-OCRv6) agree on 97% of the word sequence and 100% of the 15 figures, 97% dictionary-recognizable; different-pair recovery: tesseract produced no usable text on this scan; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
