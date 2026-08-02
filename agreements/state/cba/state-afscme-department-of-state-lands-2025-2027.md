---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon
id: state-afscme-department-of-state-lands-2025-2027
title: AFSCME Department of State Lands 2025-2027
doc_type: collective_bargaining_agreement
citation: 2025-2027 AFSCME Department of State Lands agreement
authority_level: contract
issuing_body: State of Oregon (DAS Labor Relations Unit)
union: AFSCME
term: 2025-2027
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.oregon.gov/das/HR/CBA/AFSCME%20Department%20of%20State%20Lands%202025-2027.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 00c93a020e270873da988bf9732b5748d3b05b3773513cbc9738846adb4a6d8b
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 99 pages, 297228 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 243.712
  - ORS 279.011
  - ORS 652.220
  related: []
  supersedes:
  - state-afscme-department-of-state-lands-2023-2025
tags:
- collective-bargaining
- state
- state-workforce
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.oregon.gov/das/HR/CBA/AFSCME%20Department%20of%20State%20Lands%202025-2027.pdf (retrieved 2026-08-02).

# AFSCME Department of State Lands 2025-2027

## At a glance

Collective bargaining agreement between the State of Oregon (DAS Labor Relations) and **AFSCME** for the **2025-2027** term.
- Bargaining unit (LRU chart): AFSCME DSL Department of State Lands — repr. code AX
- Ratified 2025-08-25 per the DAS LRU 2025-2027 bargaining chart (rev. 03/19/2026; committed at `_meta/state-roster-2025-2027.yml`)
- Source document: 99 pages (PDF, DAS CBA library)

This corpus is **summary-first for agreements**: the contract's text is not
reproduced here (see Curator notes), and nothing on this page states or
paraphrases the agreement's terms. Read the agreement itself at the official
source link above.

## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`): a CBA is jointly authored with private
parties, and "public record" and "freely reproducible" are not the same claim.
If the operator later flips the class, full text lands in a follow-up PR — the
committed snapshot extraction already carries what would be diffed.

Letters of agreement bound into this PDF by DAS are part of this source
snapshot; separately-published LOAs are their own documents in a later tranche.
The predecessor term's agreement is in the DAS library and is planned for the
history tranche — `supersedes` is recorded then, not faked now.

Extraction: pdftotext -layout; 99 pages, 297228 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the agreement's text cites are recorded in frontmatter
`relationships.references_external` (3 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
