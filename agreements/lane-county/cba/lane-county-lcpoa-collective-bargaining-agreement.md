---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/lane-county
id: lane-county-lcpoa-collective-bargaining-agreement
title: Lane County — LCPOA Collective Bargaining Agreement
doc_type: collective_bargaining_agreement
citation: 2025-2028 Lane County LCPOA agreement
authority_level: contract
issuing_body: Lane County
union: LCPOA
term: 2025-2028
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/LCPOA%20Collective%20Bargaining%20Agreement.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 7b44326e86f81f83e4ae72a3c42d6a2c3cb8897ee728ee070940749cc4b0a8c8
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 70 pages, 181034 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - OAR 115-040-0034
  - ORS 237.121
  - ORS 237.610
  - ORS 243.005
  - ORS 243.650
  - ORS 243.703
  - ORS 243.706
  - ORS 243.808
  - ORS 30.285
  - ORS 657B.010
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- lane-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/LCPOA%20Collective%20Bargaining%20Agreement.pdf> (retrieved 2026-08-02).

# Lane County — LCPOA Collective Bargaining Agreement

## At a glance

Collective bargaining agreement between **Lane County** and **LCPOA** — **2025-2028** term.
- Listed on the county's labor agreements index as: “LCPOA Collective Bargaining Agreement” (index archived in `_meta/discovery/`)
- Source document: 70 pages (PDF)

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
Source-manifest note: UNDATED filename overwritten in place upstream — the term is only inside the document; content hash is the only change signal.
Extraction: pdftotext -layout; 70 pages, 181034 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (10 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
