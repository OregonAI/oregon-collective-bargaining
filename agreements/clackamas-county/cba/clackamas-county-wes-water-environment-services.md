---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/clackamas-county
id: clackamas-county-wes-water-environment-services
title: Clackamas County — WES - Water Environment Services
doc_type: collective_bargaining_agreement
citation: Clackamas County WES - Water Environment Services agreement
authority_level: contract
issuing_body: Clackamas County
union: ''
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.clackamas.us/des/wes-water-environment-services-union-agreement
source_format: html
retrieved: '2026-08-02'
source_sha256: 4245cfcfac60db5edbd4c1300e552e6394ad98f7f1f0a27dd911905a794d8cb8
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: main-content text of the county's HTML page; 119226 characters extracted;
  NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 236.610
  - ORS 238.350
  - ORS 243.650
  - ORS 243.698
  - ORS 656.210
  related: []
  supersedes: []
tags:
- collective-bargaining
- county
- clackamas-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <https://www.clackamas.us/des/wes-water-environment-services-union-agreement> (retrieved 2026-08-02).

# Clackamas County — WES - Water Environment Services

## At a glance

Collective bargaining agreement between **Clackamas County** and **the signatory association**.
- Listed on the county's labor agreements index as: “WES - Water Environment Services” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: an HTML page — the county publishes this instrument's text inline rather than as a PDF

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
Source-manifest note: Intermediate HTML page for this unit/instrument — the document is a second hop behind it; resolve and hash the target at ingest.
Extraction: main-content text of the county's HTML page; 119226 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (5 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
