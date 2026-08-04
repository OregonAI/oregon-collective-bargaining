---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-foppo-loa-movement-to-a-higher-classification-pdf
title: Washington County — FOPPO LOA_Movement to a Higher Classification.pdf
doc_type: collective_bargaining_agreement
citation: Washington County FOPPO agreement
authority_level: contract
issuing_body: Washington County
union: FOPPO
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/foppo-loamovement-higher-classificationpdf/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 3b5fc1f1ed06dc388a0cc6f0f43e22b121945dbe4acc26bf2dd00eea79ae6679
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 1 pages, 2216 characters extracted; NOT human-verified
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
content_exception: 'extraction is not usable text (alphabetic ratio 0.07 < 0.45 (encoding damage)); no verbatim text can be published from it, so this document stays metadata-only until the source is re-extracted'
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.washingtoncountyor.gov/hr/documents/foppo-loamovement-higher-classificationpdf/download?inline> (retrieved 2026-08-02).

# Washington County — FOPPO LOA_Movement to a Higher Classification.pdf

## At a glance

Collective bargaining agreement between **Washington County** and **FOPPO**.
- Listed on the county's labor agreements index as: “FOPPO LOA_Movement to a Higher Classification.pdf” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 1 pages (PDF)

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

Extraction: pdftotext -layout; 1 pages, 2216 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
