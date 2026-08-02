---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/coos-county
id: coos-county-cads-cba-2026-2029
title: Coos County — CADS CBA 2026-2029
doc_type: collective_bargaining_agreement
citation: 2026-2029 Coos County CADS agreement
authority_level: contract
issuing_body: Coos County
union: CADS
term: 2026-2029
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://co.coos.or.us/files/6d9ce1874/CADS%2BCBA%2B2026-2029.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 28b7f7551e4e457fee445585a006292b788d15404b9814fba889d948913c7512
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and
  91% of the 875 figures, 99% dictionary-recognizable; 98 heading/letterhead token(s) lost
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
> source: <https://co.coos.or.us/files/6d9ce1874/CADS%2BCBA%2B2026-2029.pdf> (retrieved 2026-08-02).

# Coos County — CADS CBA 2026-2029

## At a glance

Collective bargaining agreement between **Coos County** and **CADS** — **2026-2029** term.
- Listed on the county's labor agreements index as: “CADS CBA 2026-2029” (index archived in `_meta/discovery/`)
- Source document: 37 pages (PDF)
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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 99% of the word sequence and 91% of the 875 figures, 99% dictionary-recognizable; 98 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
