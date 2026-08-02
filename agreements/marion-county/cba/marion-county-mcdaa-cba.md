---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/marion-county
id: marion-county-mcdaa-cba
title: Marion County — MCDAA CBA
doc_type: collective_bargaining_agreement
citation: Marion County MCDAA agreement
authority_level: contract
issuing_body: Marion County
union: MCDAA
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.co.marion.or.us/HR/Documents/MCDAA%20CBA.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: faabee2280e6d5b96820224cbc0684237a086af05b422fe091d92f9319386c27
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 33 pages, 93089 characters extracted; NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 243.698
  - ORS 438.010
  - ORS 653.616
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- marion-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.co.marion.or.us/HR/Documents/MCDAA%20CBA.pdf (retrieved 2026-08-02).

# Marion County — MCDAA CBA

## At a glance

Collective bargaining agreement between **Marion County** and **MCDAA**.
- Listed on the county's labor agreements index as: “MCDAA CBA” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 33 pages (PDF)

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
Extraction: pdftotext -layout; 33 pages, 93089 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (3 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
