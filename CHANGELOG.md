# Changelog — Oregon Collective Bargaining — State and County Labor Agreements

Keep a Changelog format; ISO dates. Change types: Added, Source-Updated,
Superseded, Repealed, Removed, Verified, Fixed, Security.
Repo-curation dates only — official effective dates live in frontmatter.

## [Unreleased]

### Added
- 2026-08-02 — Benton County: 3 agreements, upgraded same day from the survey's
  not-located (the careers-and-benefits page IS the index; the ONA 2025–2029
  contract was unknown to the survey). Linn and Douglas refused a third
  same-day honest-UA attempt — recorded, could-not-verify stands.
- 2026-08-02 — Two-engine OCR recovery (issue #5, the kpm standard): 52
  image-only scans ingested with tesseract + PaddleOCR corroboration —
  **Coos County fully recovered (7/7)**, Washington's MOU layer largely
  recovered (6 of its MOUs are digitally signed; OCR ran on derived copies,
  originals preserve the signatures, recorded per document). Every OCR
  document carries `text_source: ocr`, the kpm conversion_notes wording with
  both agreement rates, and WITHHELD statute citations (digits are where
  engines diverge). 8 scans held back honestly: 5 failed the two-engine gate
  (agreement 32–80%, scores printed in the ingest log) and 3 recovered under
  200 characters — human review, not ingestion.
- 2026-08-02 — Carries the state history tranche to main: its PR merged into
  its stacked base after that base had already merged (the stacked-PR trap),
  so the 36 predecessor documents never reached main until now.
- 2026-08-02 — State history tranche: 36 immediate-predecessor agreements
  (2023–2025 terms; earlier for the non-state units) as `status: superseded`,
  and `supersedes` chains linked on 30 current documents (the blackline draft
  gets `related` — a draft supersedes nothing). The 6 unlinked predecessors
  are the posting-lag units whose ratified successors DAS has not posted:
  there, the superseded document is the latest posted executed text and says
  so. The deep archive back to 2001 stays un-ingested — a decision, recorded
  in the ingester docstring, not an oversight.
- 2026-08-02 — County tranche 1: 102 documents across 9 of the 10 approved
  county publishers (Multnomah 13, Washington 22, Deschutes 18, Clackamas 20,
  Lane 11, Marion 7, Columbia 5, Jackson 3, Yamhill 3), summary-first, with
  LOAs/MOUs `related`-linked to their CBA where the union is unambiguous.
  Measured at ingest: Clackamas publishes agreement text INLINE as HTML pages
  (ingested with `source_format: html`), not behind its dochub links alone.
  **Coos has zero documents ingested**: every one of its posted CBAs is an
  image-only scan, held at the two-engine OCR gate rather than ingested
  unverifiable — as are Washington's scanned MOU layer, two Yamhill CBAs, two
  Lane modification files, and one Marion LOA (37 sources total, each a TODO
  in the ingest log; tracked as a repo issue).
- 2026-08-02 — Tranche 1: the current-term State of Oregon agreements from the
  DAS Labor Relations CBA library (32 documents: the 2025–2027 state contracts
  posted so far plus the posted non-state units), ingested summary-first per the
  class determination in `corpus.yml schema.doc_types`. Committed snapshot
  extractions under `_meta/snapshots/*.txt` (`snapshot_policy: hash-only`; PDFs
  not committed). ORS/OAR citations from each agreement's text recorded as
  `references_external`. Known absences carried by the manifest reconciliation,
  not papered over: 7 ratified 2025–2027 contracts are not yet posted by DAS
  (SEIU master final among them — only a redline "Blackline" is posted).
- 2026-08-02 — The SEIU 2025–2027 Blackline, ingested as `status: draft` by
  operator decision (reversing the first run's skip): it is a redline print,
  never presented as executed text — the document, its citation, and the
  citation resolver all say so — but it is the only state-posted copy of the
  ratified master's terms. Flips to superseded when DAS posts the final.
