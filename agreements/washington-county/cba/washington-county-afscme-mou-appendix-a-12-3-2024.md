---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-afscme-mou-appendix-a-12-3-2024
title: Washington County — AFSCME MOU_Appendix A 12.3.2024
doc_type: collective_bargaining_agreement
citation: Washington County AFSCME agreement
authority_level: contract
issuing_body: Washington County
union: AFSCME
term: ''
effective_date: ''
expiry_date: '2027-06-30'
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/afscme-mouappendix-1232024/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 01549b276e86d597b8afaeef4525a5f8f860a2d818dcf48ab4dcbb4a4c8a71aa
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 96% of the word sequence and
  78% of the 15 figures, 99% dictionary-recognizable; NOT human-verified — treat every number
  as unchecked against the source
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
> source: <https://www.washingtoncountyor.gov/hr/documents/afscme-mouappendix-1232024/download?inline> (retrieved 2026-08-02).

# Washington County — AFSCME MOU_Appendix A 12.3.2024

## At a glance

Collective bargaining agreement between **Washington County** and **AFSCME**.
- Listed on the county's labor agreements index as: “AFSCME MOU_Appendix A 12.3.2024” (index archived in `_meta/discovery/`)
- Expiry stated in the document's text: 2027-06-30
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 1 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (96% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.

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

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 96% of the word sequence and 78% of the 15 figures, 99% dictionary-recognizable; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
