---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/lane-county
id: lane-county-foppo-collective-bargaining-agreement
title: Lane County — FOPPO Collective Bargaining Agreement
doc_type: collective_bargaining_agreement
citation: 2024-2027 Lane County FOPPO agreement
authority_level: contract
issuing_body: Lane County
union: FOPPO
term: 2024-2027
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/FOPPO%20Collective%20Bargaining%20Agreement.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 796ee3af73068429af9b6ce1c72c907cf4cacab604d27ff1db40111ee779d7c0
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 53 pages, 157609 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 236.360
  - ORS 243.650
  - ORS 243.672
  - ORS 243.698
  - ORS 243.742
  - ORS 243.806
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
> source: <https://www.lanecounty.org/UserFiles/Servers/Server%5F3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/FOPPO%20Collective%20Bargaining%20Agreement.pdf> (retrieved 2026-08-02).

# Lane County — FOPPO Collective Bargaining Agreement

## At a glance

Collective bargaining agreement between **Lane County** and **FOPPO** — **2024-2027** term.
- Listed on the county's labor agreements index as: “FOPPO Collective Bargaining Agreement” (index archived in `_meta/discovery/`)
- Source document: 53 pages (PDF)

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
Extraction: pdftotext -layout; 53 pages, 157609 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (7 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
