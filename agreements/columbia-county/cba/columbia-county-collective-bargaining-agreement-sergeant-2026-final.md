---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/columbia-county
id: columbia-county-collective-bargaining-agreement-sergeant-2026-final
title: Columbia County — collective-bargaining-agreement---sergeant-2026---final
doc_type: collective_bargaining_agreement
citation: Columbia County collective-bargaining-agreement---sergeant-2026---final agreement
authority_level: contract
issuing_body: Columbia County
union: ''
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.columbiacountyor.gov/media/Human%20Resources/Union%20Contracts/collective-bargaining-agreement---sergeant-2026---final.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: bf7bf21119b873f5ec900dca7adb47f7ea4321fc22ebddd024db873e7df00bf4
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 55 pages, 138996 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - OAR 265-005-0030
  - OAR 265-015-0035
  - ORS 237.610
  - ORS 243.650
  - ORS 438.010
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- columbia-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.columbiacountyor.gov/media/Human%20Resources/Union%20Contracts/collective-bargaining-agreement---sergeant-2026---final.pdf (retrieved 2026-08-02).

# Columbia County — collective-bargaining-agreement---sergeant-2026---final

## At a glance

Collective bargaining agreement between **Columbia County** and **the signatory association**.
- Listed on the county's labor agreements index as: “collective-bargaining-agreement---sergeant-2026---final” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 55 pages (PDF)

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
Source-manifest note: Upstream URL contains literal unencoded spaces; percent-encoded here.
Extraction: pdftotext -layout; 55 pages, 138996 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (5 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
