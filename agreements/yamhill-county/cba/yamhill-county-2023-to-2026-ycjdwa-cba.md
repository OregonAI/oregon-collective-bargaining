---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/yamhill-county
id: yamhill-county-2023-to-2026-ycjdwa-cba
title: Yamhill County — 2023 to 2026 YCJDWA CBA
doc_type: collective_bargaining_agreement
citation: 2023-2026 Yamhill County YCJDWA agreement
authority_level: contract
issuing_body: Yamhill County
union: YCJDWA
term: 2023-2026
effective_date: '2023-07-01'
expiry_date: '2026-06-30'
agency_registry_slugs: []
source_url: https://www.yamhillcounty.gov/DocumentCenter/View/969/2023-to-2026-YCJDWA-CBA-PDF
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 2722fffb7abe6cc3ccb07e0d6e63d835f98febb48ee54b05e6d54ba9f7049b6b
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and
  91% of the 664 figures, 99% dictionary-recognizable; 21 heading/letterhead token(s) lost
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
> source: <https://www.yamhillcounty.gov/DocumentCenter/View/969/2023-to-2026-YCJDWA-CBA-PDF> (retrieved 2026-08-02).

# Yamhill County — 2023 to 2026 YCJDWA CBA

## At a glance

Collective bargaining agreement between **Yamhill County** and **YCJDWA** — **2023-2026** term.
- Listed on the county's labor agreements index as: “2023 to 2026 YCJDWA CBA” (index archived in `_meta/discovery/`)
- Effective date stated in the document's text: 2023-07-01
- Expiry stated in the document's text: 2026-06-30
- Source document: 51 pages (PDF)
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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and 91% of the 664 figures, 99% dictionary-recognizable; 21 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
