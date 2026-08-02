---
schema_version: 1
corpus: "oregon-collective-bargaining"
jurisdiction:         # oregon for state agreements; oregon/<slug>-county for county ones
id: 
title: ""
doc_type:             # collective_bargaining_agreement | letter_of_agreement
citation: ""          # e.g. "2025-2027 SEIU 503 State Master Agreement" — the form the
                      # parties use, never an invented numbering
authority_level: contract    # a negotiated contract, deliberately outside the
                             # statute/rule/policy chain — never implements
issuing_body: ""      # the EMPLOYER (registry slug's display name); the union is below
union: ""             # signatory union/association as the agreement names it
term: ""              # YYYY-YYYY; empty only when the document itself does not state it
effective_date: 
expiry_date:          # the term's stated end. Load-bearing: retrieval must be able to
                      # say "expired" — expired ≠ absent, current ≠ assumed
agency_registry_slugs: []    # state agreements: the agencies the bargaining units cover,
                             # resolved through the ERF agency registry (plural — one
                             # agreement, many agencies). County agreements: leave empty.
legal_authority: []
source_url: ""
source_format: 
retrieved: 
source_sha256: ""     # see the hashing contract note below — CI enforces it
last_reviewed: 
source_version: ""
status: current       # current | superseded — a superseded agreement STAYS, marked
content_mode: summary # summary-first is the corpus default (copyright gate in
                      # corpus.yml schema.doc_types). verbatim only after the operator
                      # flips the class's verbatim flag, with the basis recorded.
reproduction_basis: ""  # why this content_mode: e.g. "jointly-authored contract;
                        # summary + official link pending class determination"
conversion_notes: ""
last_verified: ""     # EMPTY STRING, never blank: blank parses as null and the
verified_by: ""       # schema types both as string, so a blank fails CI with
                      # "None is not of type 'string'". Empty = not yet verified,
                      # which is true and valid. The human reviewer fills these.
maintainer: ""
relationships:
  implements: []      # ALWAYS EMPTY in this corpus — a CBA implements nothing; the
  implemented_by: []  # corpus sits outside the authority chain by design (seed).
  references_external: []   # ORS/OAR the agreement cites (PECBA recognition clauses
                            # etc.) as citation strings — resolved into ERF as up_cites
  related: []
  supersedes: []      # the predecessor term's document id — the successor chain is
                      # how "expired, see successor" answers are built
tags: []
---

> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: {source_url} (retrieved {retrieved}).

# {title} ({citation})

## At a glance

_1–3 sentence plain-language curator summary: parties, term, what changed from the
predecessor if known. State expiry plainly when the term has lapsed._

## Full text

_Under the summary-first default this section holds NOTHING, or the limited verbatim
excerpts a future class determination permits. Everything in this section is diffed
against the pinned snapshot by CI. No paraphrase, no omission beyond what
conversion_notes declares._

## Curator notes

_Optional. Conversion caveats, context. Clearly curator-authored._

## Cross-references

_In-repo links as relative paths (e.g. the predecessor/successor agreement, the
employer's other units). Cross-corpus references go in frontmatter `relationships`
as CITATION STRINGS (e.g. `ORS 243.650`), never as local ids — the toolkit resolves
those against a sibling declared in `corpus.yml` (`siblings:`)._


<!-- HASHING CONTRACT (CI enforces this; getting it wrong fails
     corpus-verify-provenance with an error that does not explain itself).

     source_sha256 is NOT the hash of the file you downloaded, except in one
     case. The rule, from corpus_toolkit.repo.hash_snapshot:

       - if _meta/snapshots/<snapshot_id>.txt exists AND its
         whitespace-normalized content is >= 200 characters:
             sha256(normalize_ws(<that .txt>))
       - otherwise:
             sha256(raw bytes of _meta/snapshots/<snapshot_id>.<source_format>)

     The text branch exists so the hash is stable across machines: text
     extraction from a PDF varies by tool and version, so the hash is taken over
     the extraction you COMMITTED, once, at ingestion — never re-derived at
     verification time.

     Do not compute this by hand. Call the toolkit:

       from corpus_toolkit.repo import hash_snapshot
       source_sha256 = hash_snapshot(doc_id, source_format, snapshot_dir)

     Also enforced, and not obvious:
       - the filename stem MUST equal the frontmatter `id`
       - `id` must match ^[a-z0-9][a-z0-9-]+$ (lowercase; upstream filenames
         with capitals need lowercasing, and the mapping is worth recording)
       - every line under `## Full text` must appear in the snapshot IN ORDER;
         coverage below 0.70 is a hard failure
       - the disclaimer_marker string from corpus.yml must appear in the body
       - a doc_type may only live in the directory corpus.yml routes it to
-->
