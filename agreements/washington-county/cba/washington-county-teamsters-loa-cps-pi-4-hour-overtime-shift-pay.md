---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/washington-county
id: washington-county-teamsters-loa-cps-pi-4-hour-overtime-shift-pay
title: Washington County — Teamsters LOA_CPS PI 4 Hour Overtime Shift Pay
doc_type: collective_bargaining_agreement
citation: Washington County Teamsters agreement
authority_level: contract
issuing_body: Washington County
union: Teamsters
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.washingtoncountyor.gov/hr/documents/teamsters-loacps-pi-4-hour-overtime-shift-pay/download?inline
source_format: pdf
retrieved: '2026-08-02'
source_sha256: 001200c44c9103860db8abca2eedb3f16a8dc9cdf27e7cf13a5127927113e1a9
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 2 pages, 4018 characters extracted; NOT human-verified
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
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.washingtoncountyor.gov/hr/documents/teamsters-loacps-pi-4-hour-overtime-shift-pay/download?inline (retrieved 2026-08-02).

# Washington County — Teamsters LOA_CPS PI 4 Hour Overtime Shift Pay

## At a glance

Collective bargaining agreement between **Washington County** and **Teamsters**.
- Listed on the county's labor agreements index as: “Teamsters LOA_CPS PI 4 Hour Overtime Shift Pay” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 2 pages (PDF)

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

Extraction: pdftotext -layout; 2 pages, 4018 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
