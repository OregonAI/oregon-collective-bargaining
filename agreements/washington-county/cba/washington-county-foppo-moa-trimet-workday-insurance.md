---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-foppo-moa-trimet-workday-insurance
title: Washington County — FOPPO MOA_TriMet Workday Insurance
doc_type: collective_bargaining_agreement
citation: 2022-2026 Washington County FOPPO agreement
authority_level: contract
issuing_body: Washington County
union: FOPPO
term: 2022-2026
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/foppo-moatrimet-workday-insurance/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: fffb62b9d30ab6de68562dfc02886b71168cfbcda7def459fb895cfde3742e3a
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: 'no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + docTR (DBNet + CRNN)) agree on 81% of the word sequence
  and 77% of the 136 figures, 87% dictionary-recognizable; 5 heading/letterhead token(s) lost
  their word spacing in extraction and are left as-is rather than reconstructed; docTR tiebreak:
  paddleocr agreed on only 80% of the word sequence and was outvoted by the tesseract+docTR
  pair; NOT human-verified — treat every number as unchecked against the source; the source
  PDF carries a digital signature — OCR ran on a derived copy, the committed original preserves
  it'
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
> source: <https://www.washingtoncountyor.gov/hr/documents/foppo-moatrimet-workday-insurance/download?inline> (retrieved 2026-08-02).

# Washington County — FOPPO MOA_TriMet Workday Insurance

## At a glance

Collective bargaining agreement between **Washington County** and **FOPPO** — **2022-2026** term.
- Listed on the county's labor agreements index as: “FOPPO MOA_TriMet Workday Insurance” (index archived in `_meta/discovery/`)
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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + docTR (DBNet + CRNN)) agree on 81% of the word sequence and 77% of the 136 figures, 87% dictionary-recognizable; 5 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; docTR tiebreak: paddleocr agreed on only 80% of the word sequence and was outvoted by the tesseract+docTR pair; NOT human-verified — treat every number as unchecked against the source; the source PDF carries a digital signature — OCR ran on a derived copy, the committed original preserves it.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
