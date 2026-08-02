---
schema_version: 1
corpus: oregon-collective-bargaining
jurisdiction: oregon/lane-county
id: lane-county-afscme-general-cba-modifications
title: Lane County — AFSCME General CBA Modifications
doc_type: letter_of_agreement
citation: Lane County AFSCME letter of agreement
authority_level: contract
issuing_body: Lane County
union: AFSCME
term: ''
effective_date: ''
expiry_date: ''
agency_registry_slugs: []
source_url: https://www.lanecounty.org/UserFiles/Servers/Server_3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/AFSCME%20General%20CBA%20Modifications.pdf
source_format: pdf
retrieved: '2026-08-02'
source_sha256: febf1ed57654ec399f081681a74b1d3258d2284d50045c901852cd6d22da2d1d
snapshot_policy: hash-only
status: current
content_mode: summary
reproduction_basis: 'jointly-authored contract; summary + official link per the class determination
  in corpus.yml schema.doc_types (verbatim: false)'
conversion_notes: pdftotext -layout; 8 pages, 2814 characters extracted; NOT human-verified
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
- lane-county
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: https://www.lanecounty.org/UserFiles/Servers/Server_3585797/File/Government/County%20Departments/Human%20Resources/Collective%20Bargaining%20Agreements/AFSCME%20General%20CBA%20Modifications.pdf (retrieved 2026-08-02).

# Lane County — AFSCME General CBA Modifications

## At a glance

Letter of agreement / MOU under **Lane County** and **AFSCME**.
- Listed on the county's labor agreements index as: “AFSCME General CBA Modifications” (index archived in `_meta/discovery/`)
- No term is stated on the index or found in the document's front matter — `term` is left empty rather than inferred; the county presents this as its operative agreement
- Source document: 8 pages (PDF)

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
Extraction: pdftotext -layout; 8 pages, 2814 characters extracted; NOT human-verified.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` (0 citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
