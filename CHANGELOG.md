# Changelog — Oregon Collective Bargaining — State and County Labor Agreements

Keep a Changelog format; ISO dates. Change types: Added, Source-Updated,
Superseded, Repealed, Removed, Verified, Fixed, Security.
Repo-curation dates only — official effective dates live in frontmatter.

## [Unreleased]

### Fixed
- 2026-10-01 — Curator notes in all 70 state CBAs carried a static sentence
  ("...is planned for the history tranche — `supersedes` is recorded then, not
  faked now.") that went false the moment the history tranche actually ran
  (issue #100). `src/ingest_cbas.py` now derives that sentence from each
  document's own `status`, `relationships.supersedes` and
  `relationships.related` (`supersedes_note()`): the 30 `current` documents
  that carry a linked predecessor now say so and name it, without claiming
  tranche provenance the field can't prove (`retire_blackline()` also
  populates `supersedes` outside the history tranche); the SEIU blackline
  (`status: superseded`, predecessor linked under `relationships.related`
  because a draft supersedes nothing) now says its predecessor IS ingested
  and names where it's linked, instead of the same "no predecessor is
  ingested" sentence as the archive. The 37 `superseded` documents with
  nothing linked keep the truthful "no predecessor is ingested ... a recorded
  decision" wording — that's the permanent, correct state of the deep
  archive. The 3 remaining `current` documents
  (`state-afscme-oregon-emergency-management-2025-2027`,
  `state-afscme-oregon-long-term-care-ombudsman-2025-2027`,
  `state-iaff-portland-air-national-guard-firefighters-2025-2027`) do NOT get
  that wording: re-measured against `_meta/sources/state.yml` and
  `_meta/state-roster-2025-2027.yml`, each unit's immediate 2023-2025
  predecessor IS posted in the manifest, but the roster row was renamed to the
  2025-2027 title and its `match` string no longer matches the predecessor's
  older title, so `history_picks()`/`link_supersedes()` silently skip it —
  a pairing gap, not a decision. Those 3 now say that plainly and point at a
  new "KNOWN GAPS" note in the module's docstring describing the fix
  (widen the 3 `match` strings, or an explicit id override) as unresolved
  follow-up work, not done by this commit. `link_supersedes()` and
  `retire_blackline()`, which both add `supersedes`/`related` after the body
  is written, now call the new `refresh_supersedes_note()` so the sentence
  can't go stale behind them again. Bodies changed only in that sentence;
  frontmatter, `## Full text`, and `source_sha256` are untouched.

### Added
- 2026-10-01 — `_meta/employers.yml`: every `built: false` employer (25 of 37) now
  carries `status_reason` + `status_reason_date`, recording WHY it is unbuilt and
  WHEN that was established, instead of a bare `survey_status` with no reason (issue
  #8). Linn and Douglas record that the agreements ARE published and OUR fetch is
  blocked (re-tested 2026-10-01 with the corpus-toolkit `Fetcher`, still HTTP 403 for
  both); Polk, Josephine, Umatilla and Klamath record that no public copy was
  located as of the 2026-08-02 survey, worded so it never reads as "this county has
  no agreements"; the remaining 19 `not-investigated` counties record that they have
  not yet been searched. `jackson-county` (stays `built: true` / `verified`) gets a
  `status_reason` noting its one outstanding AFSCME unit and that the `mijackson.org`
  lead was Jackson County, Michigan — a dead lead, not to be re-chased. The
  registry's header records the operator's 2026-09-12 decision (issue #8) to decline
  the drafted ORS 192.311–192.478 records requests rather than send them.
- 2026-10-01 — `tests/test_employers.py`: a data-only gate on `_meta/employers.yml`'s
  absence discipline — every unbuilt row has a reason and a date, no unbuilt row
  reads as an absence claim, the could-not-verify/not-located wording matches what
  is actually true, and a built employer cannot be left marked anything but
  `verified`.

- 2026-10-01 — Marion County successor agreements (#63, amended brief): both
  `marion-mcdaa-cba` and `marion-mcjea-cba` stable URLs now serve a *successor*
  agreement, not an edited copy of what was committed. Re-verified against the
  live PDFs before acting (own text, not the manifest's stale `sha256`): MCDAA's
  footer and "EFFECTIVE FROM RATIFICATION THROUGH JUNE 30, 2029" read 2026-2029;
  MCJEA's cover states "July 1, 2026 - June 30, 2028". Ingested each as a new,
  term-suffixed document — `marion-county-mcdaa-cba-2026-2029` and
  `marion-county-mcjea-cba-2026-2028` — recording `supersedes` on the predecessor
  id, via a new one-off script (`src/ingest_marion_successors.py`) rather than a
  re-run of `src/ingest_counties.py` (whose doc_id is derived mechanically from
  the source manifest id and would have overwritten the predecessor in place —
  exactly what AGENTS.md rule 3 forbids). The predecessors,
  `marion-county-mcdaa-cba` (2023-2026) and `marion-county-mcjea-cba`
  (2024-2026), **stay committed**, flipped to `status: superseded` with a
  one-line curator note naming the successor; their text, hash and `retrieved`
  are untouched. `_meta/sources/marion.yml`'s `sha256` baselines are left for the
  reviewer to accept via `corpus-detect-changes --record-baseline` — this PR
  never runs it. **How the stable URL maps to documents:** each Marion URL now
  always serves the CURRENT agreement at the county's own index — the superseded
  document's `source_url` is the same URL, frozen at its own `retrieved` date;
  an agent resolving the live URL today gets the successor's text, and the
  predecessor is reachable only by its own id or `supersedes` edge, the same
  shape as every other successor pair in this corpus (e.g. the state tier's
  2023-2025 -> 2025-2027 chain).
- 2026-09-29 — **SEIU Master Agreement 2025-2027**, the executed agreement DAS has now
  posted, ingested verbatim (220 pages; 480 article anchors) as `current`. It `supersedes`
  the 2023-2025 master and the 2025-2027 blackline. The blackline flips from `draft` to
  `superseded`, as its own banner said it would the day the final appeared.

### Fixed
- 2026-10-01 — `_meta/employers.yml`: `benton-county` was `built: true` with
  `survey_status: not-located` and `source_url: null` — a leftover from the original
  2026-08-02 survey, before `src/discover_counties.py`'s tranche-2 hunt found
  Benton's real index (`hr.bentoncountyor.gov/careers-and-benefits/`, one navigation
  level below where the survey looked) and its 3 agreements were ingested. Flipped to
  `survey_status: verified` with the real `source_url`; `src/discover_counties.py`
  already carried the correct crawl record for this county, only the registry row
  was stale.
- 2026-09-29 — `src/ingest_cbas.py` could not ingest any agreement after the 2026-08-03
  verbatim flip: it still wrote `content_mode: summary`, which the schema refuses for
  this doc_type, so nothing has been ingested since. It now writes the promoted form
  through `promote_full_text`'s own basis and body builder. It also retires the SEIU
  blackline (`retire_blackline()`) once the executed master for its term exists.

### Source-Updated
- 2026-09-28 — `_meta/sources/state.yml` lists the **SEIU Master Agreement 2025-2027**
  (`state-seiu-master-agreement-collective-bargaining-agreement-2025-2027`), now posted by
  DAS. Ratified 2025-10-03 and carried as a POSTING-LAG since; the reconciliation now
  counts 6 lags, not 7. Not yet ingested: the corpus holds the 2023-2025 master only. The
  weekly `state-enumeration` job had been red since 2026-09-07.

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
- 2026-09-12 — Code review of #93's fix found the merge it added
  (`carry_forward_nonderivable`) ran unconditionally on the metadata-only
  stub path too, re-attaching a PRIOR extraction's `effective_date`/
  `expiry_date`/`term` to a document whose own text is deliberately withheld
  — reproduced against a real Benton document driven through the stub path,
  which then claimed both "no text is held" and dates "stated in the
  document's text" on the same page. Fixed: the stub path now carries
  forward only `union`/`agency_registry_slugs`/`reproduction_basis` (none of
  them text-derived); `term`/`effective_date`/`expiry_date` are index-only or
  empty, never inherited from an earlier, better extraction.
  Separately, the reuse short-circuit (`out.is_file() and txt.is_file()`)
  never compared the source manifest against the committed document, so a
  source re-posted at a new URL (or re-surveyed with a new title) kept its
  stale committed value forever — no flag short of `--refetch` (a full
  network re-verify) propagated it, though propagating a manifest change
  needs no network. `manifest_drift()` now compares `source_url`/`title`
  with **zero network**, and a real difference resyncs the document from the
  cached `.txt` — unless the committed document is OCR'd or a metadata-only
  stub (whose provenance cannot be honestly reconstructed without re-running
  OCR) or no raw snapshot is cached locally, either of which is reported as
  needing `--refetch` rather than silently reused or fabricated. `retrieved`
  also stopped stamping today's date unconditionally: it now advances only
  when bytes were actually fetched this run
  (`corpus_toolkit.sources.snapshots.retrieved_date`), closing the one path
  (documents with no committed `.txt` — the 5 stubs) the original fix's
  reuse short-circuit could not reach.
  "unchanged" is no longer this ingester's word for any of the above (DRIFT.md
  reserves it for a measured hash compare, which this ingester does not
  perform — that is `corpus-detect-changes`'s job, run separately and
  monthly, and is unaffected by any of this). The docstring's "safe to run"
  claim is corrected to name the one thing it always omitted: a no-flag run
  still fetches any source with no committed extraction at all (never
  ingested, or a stub) — measured today at 134 reused / 29 new (all
  Deschutes, which republished its library at new DocumentCenter ids with no
  `supersedes` edge to the 45 documents already committed under the old ones
  — tracked separately, not fixed here) / 2 stubs / 165 sources total.
  5 already-committed stub documents (`washington-county-wcpoa-moa-longevity-
  and-education-pay-3-1-2024` and 4 Deschutes MOUs) still carry a duplicated
  "METADATA-ONLY RECORD" banner from a generator bug fixed in #93's own PR —
  the generator no longer produces it, but a plain re-ingest never rewrites
  an already-committed document, so these 5 stay wrong until a `--refetch`
  (or hand) pass regenerates them; out of scope for a src-only change per
  this repo's rule against rewriting committed documents outside a reviewed
  content PR.
