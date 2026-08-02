---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon
id: state-aee-association-of-engineering-employees-2025-2027
title: AEE Association of Engineering Employees 2025-2027
doc_type: collective_bargaining_agreement
citation: 2025-2027 AEE Association of Engineering Employees agreement
authority_level: contract
issuing_body: State of Oregon (DAS Labor Relations Unit)
union: AEE
term: 2025-2027
effective_date: ''
expiry_date: '2027-06-30'
agency_registry_slugs: []
source_url: https://www.oregon.gov/das/HR/CBA/AEE%20Association%20of%20Engineering%20Employees%202025-2027.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 7bc5fdd0c37da0594f972575eb0246f95f7f69d894424b3e70cc41b905282839
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 134 pages, 414921 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 240.410
  - ORS 243.672
  - ORS 292.067
  - ORS 408.240
  - ORS 408.270
  - ORS 652.220
  - ORS 654.001
  - ORS 659A.199
  - ORS 659A.270
  - ORS 659A.283
  - ORS 659A.885
  related: []
  supersedes: []
tags:
- collective-bargaining
- state
- state-workforce
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.oregon.gov/das/HR/CBA/AEE%20Association%20of%20Engineering%20Employees%202025-2027.pdf (retrieved 2026-08-02).

# AEE Association of Engineering Employees 2025-2027

## At a glance

Collective bargaining agreement between the State of Oregon (DAS Labor Relations) and **AEE** for the **2025-2027** term.
- Bargaining unit (LRU chart): AEE Assn. of Engineering Employees — repr. code E
- Ratified 2026-01-06 per the DAS LRU 2025-2027 bargaining chart (rev. 03/19/2026; committed at `_meta/state-roster-2025-2027.yml`)
- Expiry stated in the document's text: 2027-06-30 (effectiveness is typically conditional on ratification and is recorded only when the document states a date)
- Source document: 134 pages (PDF, DAS CBA library)

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

Extraction: pdftotext -layout; 134 pages, 414921 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the agreement's text cites are recorded in frontmatter
`relationships.references_external` (11 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
