# Changelog — Oregon Collective Bargaining — State and County Labor Agreements

Keep a Changelog format; ISO dates. Change types: Added, Source-Updated,
Superseded, Repealed, Removed, Verified, Fixed, Security.
Repo-curation dates only — official effective dates live in frontmatter.

## [Unreleased]

### Added
- 2026-08-02 — The 5 remaining OCR holds ingest as METADATA-ONLY stubs
  (issue #5's terminal state): the document, its index-stated term, and the
  official link serve; NO machine reading is committed, because three engines
  disagree (32–71%) and none of their texts earned the hash. Each carries
  `content_exception`, a raw-PDF-bytes `source_sha256`, and an At a glance
  that leads with what it is. A human transcription upgrades a stub in place.
  Every approved source in every county group is now accounted for: ingested,
  stubbed, or (nothing remaining) — the OCR ledger closes.
- 2026-08-02 — docTR joins the OCR stack as the tiebreaker (and as PaddleOCR's
  partner in the different-pair recovery for scans tesseract cannot read at
  all — the policy repo's EO pattern). 6 more scans recovered: Lane's two CBA
  modification files, three Washington MOUs, Deschutes' Juneteenth MOU. 5
  genuine holds remain (agreement 32–71% across three engines) — human review,
  tracked on issue #5.
- 2026-08-02 — Jackson: the JCSSA Sheriff's Sergeants 2023–2026 agreement,
  whose only public copy is an Oregon ERB case exhibit — seeded as a
  hand-verified extra source, labeled as an exhibit copy. The survey's other
  Jackson lead was a FALSE MATCH: mijackson.org is Jackson County, MICHIGAN
  (its CBA names Michigan Council 25 AFSCME); rejected, recorded in the group
  header and the survey. Oregon Jackson County's AFSCME agreement remains
  publicly unlocated (records-request path: issue #8).
- 2026-08-02 — A real Pages site (src/build_site.py via corpus_toolkit.site),
  replacing publish-index.yml per the audits precedent — corpus-index.json
  keeps its URL; the site root stops 404ing. Coverage rendered honestly:
  verified / could-not-verify / not-located / not-investigated, never summed.
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

### Fixed
- 2026-08-27 — `src/enumerate_cbas.py` (issue #14) had no baseline-carrying step:
  every re-run of the state-tier enumerator reset all 512 recorded `sha256`
  baselines in `_meta/sources/state.yml` back to `''`, silently, because
  `build_sources()` always emits an empty hash and nothing carried the
  committed value forward. `src/discover_counties.py` got this fix for the
  12 county manifests when the same bug was found there (#58); the state
  tier — 512 of this corpus's 677 sources, three quarters of the manifest —
  did not. Reproduced: running the unfixed generator against the live DAS
  listing turned 0 blank baselines into 512; `git checkout` restored the
  file. Fixed with the same `_carry_recorded`/`_Quoted` pattern
  `discover_counties.py` already uses, so the two generators' output stays
  byte-comparable with what `corpus-detect-changes --record-baseline`
  writes. Regression-locked in `tests/` (new — this is the first pytest
  suite in this repo) for both generators; wired into the `generated` CI
  job. Verified against the live SharePoint listing: `enumerate_cbas.py
  --check` reports current, and a full re-run changes only the two
  `last_checked` dates, none of the 512 baselines.
- 2026-08-28 — Code review of the above (#14) found the regression lock did not
  lock the regression: both new test files exercised `_carry_recorded()`
  directly, so 3 of 4 ways the baseline-wipe bug returns — including deleting
  the single `main()` line that wires `_carry_recorded` into the pipeline —
  passed every test green. Fixed by adding a `main()`-driven end-to-end test
  per generator (mocks the network boundary only) and a `render()`
  quoting test for `discover_counties.py` (the state tier already had one;
  the county tier did not). Both new end-to-end tests were confirmed to fail
  against the reintroduced bugs before the fix, and pass against the fix.
  `_carry_recorded` in both generators now shares one implementation
  (`src/_manifest_baseline.py`) instead of two near-identical copies, and
  keys on `url` rather than `id` — #14's Agent Brief named `url` as the
  reliable join key and warned that an `id` match at a relocated `url` must
  not inherit that url's baseline; the shipped code carried on `id`. Neither
  generator now carries `last_checked` forward: it had frozen the state
  tier's per-source `last_checked` at its original 2026-08-02 seed date
  forever, contradicting `enumerate_cbas._strip_dates`'s own documented
  claim that the field "moves on every run by design" (confirmed live: a
  fresh re-enumeration now advances all 512 dates to the run date while
  leaving every `sha256` byte-identical). The same freeze was present in the
  county tier's `_carry_recorded`, undocumented but measurably the same bug
  (`benton.yml`'s per-source dates were stuck at 2026-08-02 through the
  2026-08-25 re-survey); fixed there too for consistency, and all 11 county
  group files were regenerated — the diff is `last_checked` moving from
  2026-08-02 to the true survey date on already-baselined sources, nothing
  else. The `.gitignore` comment for `changed-sources.tsv`/`source-outcomes.json`
  cited "AGENTS.md: both are public surface" — AGENTS.md contains no such
  sentence; reworded to state the rationale directly. `pip install pytest`
  in the CI `generated` job was unpinned and undocumented (this repo pins
  everything else); pytest is now pinned in `requirements-dev.txt` and the
  suite runs in its own `tests` job. Opened #65 for 6 fetch failures (2
  Multnomah, 4 Yamhill) that a full live drift run surfaced but that match
  no open issue and sit under the toolkit's systemic-failure threshold, so
  they are currently invisible to every gate.
  **Left open, honestly:** #14's own acceptance criteria "Issues #17–#41 are
  closed as false positives" and "the next scheduled run opens no
  source-change issues" are not both met yet. #17–#22 are closed; #23–#41 and
  #43–#46 (23 issues) are still open — this session's tooling permissions did
  not allow closing GitHub issues, so they need a human or a differently
  -permissioned session to close them with the same "false positive of #14"
  reasoning already used on #17–#22. And #64 (19 Clackamas sources changing
  together, likely a sitewide alert banner) and #63 (Marion's MCDAA CBA, a
  genuine content change) mean the next scheduled run WILL open source-change
  issues for real, current drift — expected and correct, not a regression,
  but #14 should not be read as having silenced the job; #64 is what would
  silence the Clackamas noise, and it is diagnosed but not yet fixed.
