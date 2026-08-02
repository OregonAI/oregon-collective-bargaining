---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/marion-county
id: marion-county-mcssa-cba
title: Marion County — MCSSA CBA
doc_type: collective_bargaining_agreement
citation: Marion County MCSSA agreement
authority_level: contract
issuing_body: Marion County
union: MCSSA
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.co.marion.or.us/HR/Documents/MCSSA%20CBA.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 26c502e0f33d83bbde57d36f8f7b6ef01f1a45810cdafe0b10cec15d50462077
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 66 pages, 113559 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 131.930
  - ORS 236.360
  - ORS 243.808
  - ORS 438.010
  - ORS 659A.043
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- marion-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.co.marion.or.us/HR/Documents/MCSSA%20CBA.pdf (retrieved 2026-08-02).

# Marion County — MCSSA CBA

## At a glance

Collective bargaining agreement between **Marion County** and **MCSSA**.
- Listed on the county's labor agreements index as: “MCSSA CBA” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 66 pages (PDF)

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
Extraction: pdftotext -layout; 66 pages, 113559 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (5 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
