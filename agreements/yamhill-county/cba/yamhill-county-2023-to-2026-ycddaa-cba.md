---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/yamhill-county
id: yamhill-county-2023-to-2026-ycddaa-cba
title: Yamhill County — 2023 to 2026 YCDDAA CBA
doc_type: collective_bargaining_agreement
citation: 2023-2026 Yamhill County YCDDAA agreement
authority_level: contract
issuing_body: Yamhill County
union: YCDDAA
term: 2023-2026
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.yamhillcounty.gov/DocumentCenter/View/968/2023-to-2026-YCDDAA-CBA-PDF
source_format: pdf
retrieved: '2026-08-02'
source_sha256: b6dde97464abfc48c022f251ebbdb551b35ad8c1a07dd7debe7819f471fc3907
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and
  91% of the 524 figures, 99% dictionary-recognizable; 18 heading/letterhead token(s) lost
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
- yamhill-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.yamhillcounty.gov/DocumentCenter/View/968/2023-to-2026-YCDDAA-CBA-PDF> (retrieved 2026-08-02).

# Yamhill County — 2023 to 2026 YCDDAA CBA

## At a glance

Collective bargaining agreement between **Yamhill County** and **YCDDAA** — **2023-2026** term.
- Listed on the county's labor agreements index as: “2023 to 2026 YCDDAA CBA” (index archived in `_meta/discovery/`)
- Source document: 31 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (99% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and 91% of the 524 figures, 99% dictionary-recognizable; 18 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
