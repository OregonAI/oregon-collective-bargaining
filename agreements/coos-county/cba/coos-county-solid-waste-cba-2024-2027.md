---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/coos-county
id: coos-county-solid-waste-cba-2024-2027
title: Coos County — Solid Waste CBA 2024- 2027
doc_type: collective_bargaining_agreement
citation: 2024-2027 Coos County Solid Waste CBA 2024- 2027 agreement
authority_level: contract
issuing_body: Coos County
union: ''
term: 2024-2027
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://co.coos.or.us/files/eaf81a903/solid%5Fwaste%5Fcba%5F2024-%5F2027.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 7e81cb415396e9169b1e54a73a1c3f64eca7a29f90bfb4f0ac369220d0c4dc6d
snapshot_policy: hash-only
status: current
content_mode: summary
text_source: ocr
reproduction_basis: 'jointly-authored contract, class verbatim: true in corpus.yml — but
  this source is an image-only scan, so no verbatim extraction exists to mirror; metadata
  plus official link, per the content_exception below'
content_exception: 'image-only scan read by OCR. The reading passed three-engine
  corroboration and is committed as the snapshot, but it is NOT published as verbatim text:
  the two engines agree on only 81% of this document''s 427 figures, and it carries 1
  dollar amount(s) — wage rates, step schedules or premium pay, which is what a reader acts
  on. A misread digit there is plausible and indistinguishable from the real figure.
  Metadata and hash are trustworthy; the executed text is at source_url. Operator decision
  on #91, 2026-09-12: convert where measured figure agreement is under 95% AND dollar
  amounts are published.'
conversion_notes: no text layer in the source PDF; text recovered by OCR. Two independent
  engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 98% of the word sequence and
  81% of the 427 figures, 98% dictionary-recognizable; 16 heading/letterhead token(s) lost
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

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a non-authoritative
> mirror of the agreement's text, not the official record. Verify against the official
> source: <https://co.coos.or.us/files/eaf81a903/solid%5Fwaste%5Fcba%5F2024-%5F2027.pdf> (retrieved 2026-08-02).

# Coos County — Solid Waste CBA 2024- 2027

## At a glance

Collective bargaining agreement between **Coos County** and **the signatory association** — **2024-2027** term.
- Listed on the county's labor agreements index as: “Solid Waste CBA 2024- 2027” (index archived in `_meta/discovery/`)
- Source document: 24 pages (PDF)
- **The source is an image-only scan.** Its committed text is a machine reading corroborated by two independent OCR engines (98% word-sequence agreement — see conversion_notes). Dates and terms above come from that reading; statute citations are deliberately not extracted, because digits are where engines diverge.


## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`). `status: current` records that this
document sits on the county's own operative labor-agreements index at ingest
time — county pages, unlike the DAS library, publish no history, so currency
rests on the index and on content-hash drift detection.

Extraction: no text layer in the source PDF; text recovered by OCR. Two independent engines (tesseract (ocrmypdf) + paddleocr PP-OCRv6) agree on 98% of the word sequence and 81% of the 427 figures, 98% dictionary-recognizable; 16 heading/letterhead token(s) lost their word spacing in extraction and are left as-is rather than reconstructed; NOT human-verified — treat every number as unchecked against the source.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.

