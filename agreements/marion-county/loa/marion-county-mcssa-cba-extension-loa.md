---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/marion-county
id: marion-county-mcssa-cba-extension-loa
title: Marion County — MCSSA CBA Extension LOA
doc_type: letter_of_agreement
citation: 2026-2027 Marion County MCSSA letter of agreement
authority_level: contract
issuing_body: Marion County
union: MCSSA
term: 2026-2027
effective_date: '2026-07-01'
expiry_date: '2027-06-30'
agency_registry_slugs: []
source_url: https://www.co.marion.or.us/HR/Documents/MCSSA%20CBA%20Extension%20LOA.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: decc48d7c65e089093b4534fb14d50d609700fffd2a259e20dc5266a3f59534f
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 98% of the word sequence and
  86% of the 58 figures, 98% dictionary-recognizable; NOT human-verified — treat every number
  as unchecked against the source
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external: []
  related:
  - marion-county-mcssa-cba
  supersedes: []
tags:
- collective-bargaining
- county
- marion-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.co.marion.or.us/HR/Documents/MCSSA%20CBA%20Extension%20LOA.pdf> (retrieved 2026-08-02).

# Marion County — MCSSA CBA Extension LOA

## At a glance

Letter of agreement / MOU under **Marion County** and **MCSSA** — **2026-2027** term.
- Listed on the county's labor agreements index as: “MCSSA CBA Extension LOA” (index archived in `_meta/discovery/`)
- Effective date stated in the document's text: 2026-07-01
- Expiry stated in the document's text: 2027-06-30
- Source document: 2 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (98% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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
Source-manifest note: UNDATED filename overwritten in place upstream — same hashing mandate as Lane.
Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 98% of the word sequence and 86% of the 58 figures, 98% dictionary-recognizable; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
