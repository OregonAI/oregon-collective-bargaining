---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/marion-county
id: marion-county-mcea-cba
title: Marion County — MCEA CBA
doc_type: collective_bargaining_agreement
citation: 2024-2026 Marion County MCEA agreement
authority_level: contract
issuing_body: Marion County
union: MCEA
term: 2024-2026
effective_date: '2024-07-01'
expiry_date: '2026-06-30'
agency_registry_slugs: []
source_url: https://www.co.marion.or.us/HR/Documents/MCEA%20CBA.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 83ac9c572ec46a0abe70c38bc612e8f3aadfb5830607e9fa99188f84813ee5f0
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 57 pages, 154124 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 243.650
  - ORS 243.736
  - ORS 243.782
  - ORS 652.120
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- marion-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.co.marion.or.us/HR/Documents/MCEA%20CBA.pdf (retrieved 2026-08-02).

# Marion County — MCEA CBA

## At a glance

Collective bargaining agreement between **Marion County** and **MCEA** — **2024-2026** term.
- Listed on the county's labor agreements index as: “MCEA CBA” (index archived in `_meta/discovery/`)
- Effective date stated in the document's text: 2024-07-01
- Expiry stated in the document's text: 2026-06-30
- Source document: 57 pages (PDF)

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
Extraction: pdftotext -layout; 57 pages, 154124 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (4 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
