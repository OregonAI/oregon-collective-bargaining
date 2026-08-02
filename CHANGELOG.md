# Changelog — Oregon Collective Bargaining — State and County Labor Agreements

Keep a Changelog format; ISO dates. Change types: Added, Source-Updated,
Superseded, Repealed, Removed, Verified, Fixed, Security.
Repo-curation dates only — official effective dates live in frontmatter.

## [Unreleased]

### Added
- 2026-08-02 — Tranche 1: the current-term State of Oregon agreements from the
  DAS Labor Relations CBA library (32 documents: the 2025–2027 state contracts
  posted so far plus the posted non-state units), ingested summary-first per the
  class determination in `corpus.yml schema.doc_types`. Committed snapshot
  extractions under `_meta/snapshots/*.txt` (`snapshot_policy: hash-only`; PDFs
  not committed). ORS/OAR citations from each agreement's text recorded as
  `references_external`. Known absences carried by the manifest reconciliation,
  not papered over: 7 ratified 2025–2027 contracts are not yet posted by DAS
  (SEIU master final among them — only a redline "Blackline" is posted, and it
  is deliberately not ingested).
