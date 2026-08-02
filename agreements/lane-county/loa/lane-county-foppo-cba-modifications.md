---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/lane-county
id: lane-county-foppo-cba-modifications
title: Lane County — FOPPO CBA Modifications
doc_type: letter_of_agreement
citation: 2024-2027 Lane County FOPPO letter of agreement
authority_level: contract
issuing_body: Lane County
union: FOPPO
term: 2024-2027
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/FOPPO%20CBA%20Modifications.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: bcd8588b566112702a4b24c7c7e2f8dd1064c060a472d7da02252251c296250a
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 92% of the word sequence and
  77% of the 17 figures, 98% dictionary-recognizable; NOT human-verified — treat every number
  as unchecked against the source
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external: []
  related:
  - lane-county-foppo-collective-bargaining-agreement
  supersedes: []
tags:
- collective-bargaining
- county
- lane-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/FOPPO%20CBA%20Modifications.pdf> (retrieved 2026-08-02).

# Lane County — FOPPO CBA Modifications

## At a glance

Letter of agreement / MOU under **Lane County** and **FOPPO** — **2024-2027** term.
- Listed on the county's labor agreements index as: “FOPPO CBA Modifications” (index archived in `_meta/discovery/`)
- Source document: 1 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (92% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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
Source-manifest note: UNDATED filename overwritten in place upstream — the term is only inside the document; content hash is the only change signal.
Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 92% of the word sequence and 77% of the 17 figures, 98% dictionary-recognizable; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
