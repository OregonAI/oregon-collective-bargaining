---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/jackson-county
id: jackson-county-federation-of-oregon-parole-and-probation-officers-foppo-labor-agreement
title: Jackson County — Federation of Oregon Parole and Probation Officers (FOPPO) Labor Agreement
doc_type: collective_bargaining_agreement
citation: 2025-2028 Jackson County FOPPO agreement
authority_level: contract
issuing_body: Jackson County
union: FOPPO
term: 2025-2028
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://jacksoncountyor.gov/Document%20Center/Departments/Human%20Resources/Labor%20Agreements/2025-2028%20Jackson%20County-FOPPO%20Signed%20CBA.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 4d880c0091af5be20e4ba15beab753ef878f7915f47c6c8268849c7f89755cc7
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 52 pages, 116664 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 236.350
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- jackson-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://jacksoncountyor.gov/Document%20Center/Departments/Human%20Resources/Labor%20Agreements/2025-2028%20Jackson%20County-FOPPO%20Signed%20CBA.pdf (retrieved 2026-08-02).

# Jackson County — Federation of Oregon Parole and Probation Officers (FOPPO) Labor Agreement

## At a glance

Collective bargaining agreement between **Jackson County** and **FOPPO** — **2025-2028** term.
- Listed on the county's labor agreements index as: “Federation of Oregon Parole and Probation Officers (FOPPO) Labor Agreement” (index archived in `_meta/discovery/`)
- Source document: 52 pages (PDF)

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
Extraction: pdftotext -layout; 52 pages, 116664 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (1 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
