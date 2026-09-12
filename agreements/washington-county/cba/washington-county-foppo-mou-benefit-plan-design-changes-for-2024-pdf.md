---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-foppo-mou-benefit-plan-design-changes-for-2024-pdf
title: Washington County — FOPPO MOU_Benefit Plan Design Changes for 2024.pdf
doc_type: collective_bargaining_agreement
citation: Washington County FOPPO agreement
authority_level: contract
issuing_body: Washington County
union: FOPPO
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/foppo-moubenefit-plan-design-changes-2024pdf/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 63b70f2bde6f1d434e7d47dd8f4bb73baf09eaa64ef5702b6cf83fbaac909c1a
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract, class verbatim: true in corpus.yml — but
  this source is an image-only scan, so no verbatim extraction exists to mirror; metadata
  plus official link, per the content_exception below'
content_exception: 'image-only scan read by OCR. The reading passed three-engine
  corroboration and is committed as the snapshot, but it is NOT published as verbatim text:
  the two engines agree on only 86% of this document''s 19 figures, and it carries 1
  dollar amount(s) — wage rates, step schedules or premium pay, which is what a reader acts
  on. A misread digit there is plausible and indistinguishable from the real figure.
  Metadata and hash are trustworthy; the executed text is at source_url. Operator decision
  on #91, 2026-09-12: convert where measured figure agreement is under 95% AND dollar
  amounts are published.'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 96% of the word sequence and
  86% of the 19 figures, 100% dictionary-recognizable; NOT human-verified — treat every number
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

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a non-authoritative
> mirror of the agreement's text, not the official record. Verify against the official
> source: <https://www.washingtoncountyor.gov/hr/documents/foppo-moubenefit-plan-design-changes-2024pdf/download?inline> (retrieved 2026-08-02).

# Washington County — FOPPO MOU_Benefit Plan Design Changes for 2024.pdf

## At a glance

Collective bargaining agreement between **Washington County** and **FOPPO**.
- Listed on the county's labor agreements index as: “FOPPO MOU_Benefit Plan Design Changes for 2024.pdf” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 1 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (96% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.


## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`). `status: current` records that this
document sits on the county's own operative labor-agreements index at ingest
time — county pages, unlike the DAS library, publish no history, so currency
rests on the index and on content-hash drift detection.

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 96% of the word sequence and 86% of the 19 figures, 100% dictionary-recognizable; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.

