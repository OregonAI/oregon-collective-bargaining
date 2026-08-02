---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon
id: state-afscme-non-state-child-care-providers-together-2025-2029
title: AFSCME Non State Child Care Providers Together 2025-2029
doc_type: collective_bargaining_agreement
citation: 2025-2029 AFSCME Non State Child Care Providers Together agreement
authority_level: contract
issuing_body: State of Oregon (DAS Labor Relations Unit)
union: AFSCME
term: 2025-2029
effective_date: ''
expiry_date: '2029-06-30'
agency_registry_slugs: []
source_url: https://www.oregon.gov/das/HR/CBA/AFSCME%20Non%20State%20Child%20Care%20Providers%20Together%202025-2029.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: e05c15f3560c8d721a9c53e51b532455da33fed60d6750c03cb5d99b56e8a07e
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 48 pages, 87079 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - OAR 414-075-0300
  - OAR 414-175-0075
  - ORS 243.698
  - ORS 243.712
  - ORS 243.746
  - ORS 329A.500
  - ORS 657A.430
  related: []
  supersedes:
  - state-afscme-non-state-childcare-providers-together-2021-2025
tags:
- collective-bargaining
- state
- non-state-unit
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.oregon.gov/das/HR/CBA/AFSCME%20Non%20State%20Child%20Care%20Providers%20Together%202025-2029.pdf (retrieved 2026-08-02).

# AFSCME Non State Child Care Providers Together 2025-2029

## At a glance

Collective bargaining agreement between the State of Oregon (DAS Labor Relations) and **AFSCME** for the **2025-2029** term.
- Bargaining unit (LRU chart): AFSCME Child Care Providers Together
- Ratified 2025-11-22 per the DAS LRU 2025-2027 bargaining chart (rev. 03/19/2026; committed at `_meta/state-roster-2025-2027.yml`)
- A NON-STATE bargaining unit on the DAS chart: the workers are not state employees; DAS bargains the agreement.
- Expiry stated in the document's text: 2029-06-30 (effectiveness is typically conditional on ratification and is recorded only when the document states a date)
- Source document: 48 pages (PDF, DAS CBA library)

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

Extraction: pdftotext -layout; 48 pages, 87079 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the agreement's text cites are recorded in frontmatter
`relationships.references_external` (7 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
