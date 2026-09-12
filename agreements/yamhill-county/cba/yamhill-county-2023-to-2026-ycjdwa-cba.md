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
source_sha256: 80b9398a9879f912dd573418097fb82755517a2300ff9c1aae69422b3dbda139
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract, class verbatim: true in corpus.yml — but
  this source is an image-only scan, so no verbatim extraction exists to mirror; metadata
  plus official link, per the content_exception below'
content_exception: 'image-only scan read by OCR. The reading passed three-engine
  corroboration and is committed as the snapshot, but it is NOT published as verbatim text:
  the two engines agree on only 91% of this document''s 664 figures, and it carries 5
  dollar amount(s) — wage rates, step schedules or premium pay, which is what a reader acts
  on. A misread digit there is plausible and indistinguishable from the real figure.
  Metadata and hash are trustworthy; the executed text is at source_url. Operator decision
  on #91, 2026-09-12: convert where measured figure agreement is under 95% AND dollar
  amounts are published.'
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

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a non-authoritative
> mirror of the agreement's text, not the official record. Verify against the official
> source: <https://www.yamhillcounty.gov/DocumentCenter/View/969/2023-to-2026-YCJDWA-CBA-PDF> (retrieved 2026-08-02).

# Yamhill County — 2023 to 2026 YCJDWA CBA

## At a glance

Collective bargaining agreement between **Yamhill County** and **YCJDWA** — **2023-2026** term.
- Listed on the county's labor agreements index as: “2023 to 2026 YCJDWA CBA” (index archived in `_meta/discovery/`)
- Effective date stated in the document's text: 2023-07-01
- Expiry stated in the document's text: 2026-06-30
- Source document: 51 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (99% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.


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

