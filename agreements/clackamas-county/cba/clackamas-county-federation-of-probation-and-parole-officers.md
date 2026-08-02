---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/clackamas-county
id: clackamas-county-federation-of-probation-and-parole-officers
title: Clackamas County — Federation of Probation and Parole Officers
doc_type: collective_bargaining_agreement
citation: 2022-2025 Clackamas County Federation of Probation and Parole Officers agreement
authority_level: contract
issuing_body: Clackamas County
union: ''
term: 2022-2025
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.clackamas.us/des/foppo-contract
source_format: html
retrieved: '2026-08-02'
source_sha256: bec44b48b55f207515cee7985424d18ff1169aae428cd5f028a1b5c98a77e2d9
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: main-content text of the county's HTML page; 128126 characters extracted;
  NOT human-verified
last_verified: ''
verified_by: ''
maintainer: '@morficflux'
relationships:
  implements: []
  implemented_by: []
  references_external:
  - ORS 238.015
  - ORS 654.001
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
> source: <https://www.clackamas.us/des/foppo-contract> (retrieved 2026-08-02).

# Clackamas County — Federation of Probation and Parole Officers

## At a glance

Collective bargaining agreement between **Clackamas County** and **the signatory association** — **2022-2025** term.
- Listed on the county's labor agreements index as: “Federation of Probation and Parole Officers” (index archived in `_meta/discovery/`)
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
Extraction: main-content text of the county's HTML page; 128126 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (3 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
