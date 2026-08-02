---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/coos-county
id: coos-county-prosecuting-attorneys-cba-2024-2027
title: Coos County — Prosecuting Attorneys CBA 2024-2027
doc_type: collective_bargaining_agreement
citation: 2024-2027 Coos County Prosecuting agreement
authority_level: contract
issuing_body: Coos County
union: Prosecuting
term: 2024-2027
effective_date: '2024-07-01'
expiry_date: '2027-06-30'
agency_registry_slugs: []
source_url: https://co.coos.or.us/files/3ed43907f/prosecuting%5Fattorneys%5Fcba%5F2024-2027.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 153e0c1355777ae35a1b9858cc7cddff759b3e33ffc8f8115a92ee4569e06e68
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 95% of the word sequence and
  64% of the 439 figures, 96% dictionary-recognizable; 11 heading/letterhead token(s) lost
  their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified
  — treat every number as unchecked against the source
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
- coos-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://co.coos.or.us/files/3ed43907f/prosecuting%5Fattorneys%5Fcba%5F2024-2027.pdf> (retrieved 2026-08-02).

# Coos County — Prosecuting Attorneys CBA 2024-2027

## At a glance

Collective bargaining agreement between **Coos County** and **Prosecuting** — **2024-2027** term.
- Listed on the county's labor agreements index as: “Prosecuting Attorneys CBA 2024-2027” (index archived in `_meta/discovery/`)
- Effective date stated in the document's text: 2024-07-01
- Expiry stated in the document's text: 2027-06-30
- Source document: 26 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (95% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 95% of the word sequence and 64% of the 439 figures, 96% dictionary-recognizable; 11 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
