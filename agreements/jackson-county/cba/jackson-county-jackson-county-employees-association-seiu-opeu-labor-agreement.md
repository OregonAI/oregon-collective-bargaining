---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/jackson-county
id: jackson-county-jackson-county-employees-association-seiu-opeu-labor-agreement
title: Jackson County — Jackson County Employees' Association (SEIU, OPEU) Labor Agreement
doc_type: collective_bargaining_agreement
citation: Jackson County SEIU agreement
authority_level: contract
issuing_body: Jackson County
union: SEIU
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://jacksoncountyor.gov/Document%20Center/Departments/Human%20Resources/Labor%20Agreements/Jackson%20County-SEIU%20CBA%20FINAL%20SIGNED.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: f49b88ad5dcfc524a9ad0cd9e9c8e4b02f3444d43ae8ee599544c83d22d6017a
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 43 pages, 134968 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - OAR 437-001-0765
  - ORS 238.350
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- jackson-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://jacksoncountyor.gov/Document%20Center/Departments/Human%20Resources/Labor%20Agreements/Jackson%20County-SEIU%20CBA%20FINAL%20SIGNED.pdf> (retrieved 2026-08-02).

# Jackson County — Jackson County Employees' Association (SEIU, OPEU) Labor Agreement

## At a glance

Collective bargaining agreement between **Jackson County** and **SEIU**.
- Listed on the county's labor agreements index as: “Jackson County Employees' Association (SEIU, OPEU) Labor Agreement” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 43 pages (PDF)

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
Source-manifest note: Upstream href carries a ?t= cache-buster (dropped here — it moves on every re-upload, so its CHANGE is itself an update signal worth checking at re-discovery).
Extraction: pdftotext -layout; 43 pages, 134968 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (2 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
