"""`src/ingest_counties.py` re-ingest safety (oregon-collective-bargaining#93).

A bulk re-ingest (`python3 src/ingest_counties.py --ocr`, no `--only`, no `--refetch`)
rewrote 29 already-committed documents: 604 insertions, 35,777 deletions. Two
independent faults, both fixed here:

  1. The ingester reached the network even without `--refetch`, so `retrieved` and
     `source_sha256` moved on every run regardless of whether the source actually
     changed -- making hash churn indistinguishable from genuine upstream drift.
  2. `union`, `term`, `effective_date`, `expiry_date`, `agency_registry_slugs` and
     `reproduction_basis` are not derivable from the PDF on every run (they come
     from the county index, the document's own text, or a curation pass this
     ingester never performs) -- so a run that could not reproduce one wrote a
     poorer document instead of carrying the committed value forward. Same
     whole-row-survival shape as executive-regulatory-frameworks#353's
     `preserve_manual()`.

Same seam decision as `tests/test_discover_counties.py` / `tests/test_enumerate_cbas.py`:
read real committed values out of `agreements/benton-county/cba/...` (Benton is the
smallest county group -- 3 sources, all already ingested) rather than a hand-authored
fixture, and drive `main()` itself against a scratch copy of that real state for the
regression locks -- not just the helper functions in isolation. `agency_registry_slugs`
is the one field with no real non-empty example anywhere in this corpus yet (this
ingester has always hardcoded it to `[]`; nothing has curated it); tests that need a
non-empty value for it say so and use a clearly-synthetic one.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import ingest_counties  # noqa: E402

REAL_BENTON_DOC = (REPO_ROOT / "agreements" / "benton-county" / "cba"
                   / "benton-county-oregon-nurses-association-july-1-2025-june-30-2029.md")
REAL_BENTON_SOURCES = REPO_ROOT / "_meta" / "sources" / "benton.yml"


def _real_committed_frontmatter() -> dict:
    fm, _ = ingest_counties.parse_frontmatter(REAL_BENTON_DOC)
    return fm


# -- carry_forward_nonderivable ---------------------------------------------------

def test_carry_forward_preserves_every_nonderivable_field_when_fresh_has_none():
    """A run that could not re-derive ANY of the six fields (own_dates found no
    span, union_of matched nothing, no curation) must not blank a committed
    document -- every field carries forward from the real Benton ONA contract."""
    existing = _real_committed_frontmatter()
    fresh = {"union": "", "term": "", "effective_date": "", "expiry_date": "",
             "agency_registry_slugs": [], "reproduction_basis": ""}

    merged = ingest_counties.carry_forward_nonderivable(fresh, existing)

    assert merged["union"] == existing["union"] == "Oregon Nurses"
    assert merged["term"] == existing["term"] == "2025-2029"
    assert merged["effective_date"] == existing["effective_date"] == "2025-07-01"
    assert merged["expiry_date"] == existing["expiry_date"] == "2029-06-30"
    assert merged["reproduction_basis"] == existing["reproduction_basis"]


def test_carry_forward_prefers_a_fresh_value_over_the_committed_one():
    """This run's own finding wins -- carrying forward is a fallback for a gap, not
    a standing override of a real re-derivation (e.g. the document's own text now
    states a clearer term than the index did originally)."""
    existing = _real_committed_frontmatter()
    fresh = {"union": "Oregon Nurses", "term": "2026-2030", "effective_date": "",
             "expiry_date": "", "agency_registry_slugs": [], "reproduction_basis": ""}

    merged = ingest_counties.carry_forward_nonderivable(fresh, existing)

    assert merged["term"] == "2026-2030", "a freshly re-derived term must not be overwritten"
    assert merged["effective_date"] == existing["effective_date"], (
        "a field this run left empty must still carry forward")


def test_carry_forward_is_a_noop_with_no_existing_document():
    """A document ingested for the first time has nothing to carry forward from --
    `existing=None` must leave `fresh` exactly as the caller built it."""
    fresh = {"union": "", "term": "", "effective_date": "", "expiry_date": "",
             "agency_registry_slugs": [], "reproduction_basis": ""}

    merged = ingest_counties.carry_forward_nonderivable(fresh, None)

    assert merged == fresh


def test_carry_forward_preserves_agency_registry_slugs_never_derived_by_this_ingester():
    """`agency_registry_slugs` has no real non-empty example in this corpus yet --
    this ingester has always hardcoded it to `[]` (that is itself the bug: it can
    never SEE a human's curation on a later run). A synthetic non-empty value here
    stands in for a curated row so the merge is exercised at all."""
    existing = {"agency_registry_slugs": ["oregon-health-authority"], "union": "",
                "term": "", "effective_date": "", "expiry_date": "",
                "reproduction_basis": ""}
    fresh = {"agency_registry_slugs": [], "union": "", "term": "",
             "effective_date": "", "expiry_date": "", "reproduction_basis": ""}

    merged = ingest_counties.carry_forward_nonderivable(fresh, existing)

    assert merged["agency_registry_slugs"] == ["oregon-health-authority"]


# -- load_existing ------------------------------------------------------------------

def test_load_existing_reads_the_real_committed_document():
    fm = ingest_counties.load_existing(REAL_BENTON_DOC)

    assert fm is not None
    assert fm["union"] == "Oregon Nurses"
    assert fm["term"] == "2025-2029"
    assert fm["source_sha256"] == (
        "546d06fd17744b0f80993a771a03c7fd9132361703f8700c8f0ab5dd4dbb9783")


def test_load_existing_returns_none_for_a_document_never_ingested():
    assert ingest_counties.load_existing(
        REPO_ROOT / "agreements" / "benton-county" / "cba"
        / "benton-county-a-document-nobody-has-ever-ingested.md") is None


# -- manifest_drift (finding 2's no-network compare) --------------------------------

def test_manifest_drift_empty_when_nothing_changed():
    existing = {"source_url": "https://example.org/a.pdf", "title": "A County — A Title"}
    rec = {"url": "https://example.org/a.pdf", "title": "A Title", "format": "pdf"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(existing, rec, county) == []


def test_manifest_drift_flags_a_changed_source_url_for_a_pdf_source():
    existing = {"source_url": "https://example.org/OLD.pdf", "title": "A County — A Title"}
    rec = {"url": "https://example.org/NEW.pdf", "title": "A Title", "format": "pdf"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(existing, rec, county) == ["source_url"]


def test_manifest_drift_flags_a_changed_title():
    existing = {"source_url": "https://example.org/a.pdf", "title": "A County — Old Title"}
    rec = {"url": "https://example.org/a.pdf", "title": "New Title", "format": "pdf"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(existing, rec, county) == ["title"]


def test_manifest_drift_is_empty_with_no_existing_document():
    rec = {"url": "https://example.org/a.pdf", "title": "A Title", "format": "pdf"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(None, rec, county) == []


def test_manifest_drift_does_not_flag_source_url_for_an_html_source_with_a_resolved_link():
    """An HTML-format source whose index page links a document (Clackamas's dochub
    pattern, Benton's wp-content pattern -- both recorded in this ingester's own
    docstring) legitimately commits a DIFFERENT `source_url` than `rec['url']`: the
    manifest's `url` is the intermediate index page, but the committed document's
    `source_url` is whichever URL was actually fetched (the page itself, or a
    resolved link out of it) -- which one depends on a network fetch this compare
    must not make. Comparing them directly would false-positive on every such
    source: reproduced against the REAL committed data (found while verifying
    finding 2's fix against the whole corpus, not invented) -- 4 real Clackamas
    documents (`clackamas-county-employee-association` and 3 siblings) commit their
    resolved dochub link as `source_url` while `_meta/sources/clackamas.yml` still
    (correctly) carries the intermediate `https://www.clackamas.us/des/...` page as
    `url`. `title` is still checked -- it never depends on which URL was fetched."""
    existing = {"source_url": "https://dochub.clackamas.us/documents/drupal/abc123",
                "title": "A County — Employee Association"}
    rec = {"url": "https://www.clackamas.us/des/employee-association",
          "title": "Employee Association", "format": "html"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(existing, rec, county) == []


def test_manifest_drift_still_flags_a_title_change_for_an_html_source():
    existing = {"source_url": "https://dochub.clackamas.us/documents/drupal/abc123",
                "title": "A County — Old Title"}
    rec = {"url": "https://www.clackamas.us/des/employee-association",
          "title": "New Title", "format": "html"}
    county = {"name": "A County"}

    assert ingest_counties.manifest_drift(existing, rec, county) == ["title"]


# -- classify (the --check seam) -----------------------------------------------------

def test_classify_a_never_ingested_source_as_new(tmp_path):
    out = tmp_path / "new-doc.md"
    txt = tmp_path / "new-doc.txt"
    assert "new" in ingest_counties.classify(out, txt, refetch=False)


def test_classify_an_ingested_source_with_a_committed_snapshot_as_reused_no_network(
        tmp_path):
    """Finding 3 (code review, fix/safe-reingest): DRIFT.md reserves "unchanged" for
    a measured hash compare, which classify() never performs when called with no
    `rec`/`county` to compare against (this call shape: nothing was compared at
    all) -- "reused, no network" is the honest claim here, not "unchanged"."""
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text("---\n---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")

    result = ingest_counties.classify(out, txt, refetch=False)

    assert "unchanged" not in result
    assert "reused" in result
    assert "no network" in result


def test_classify_reports_manifest_match_as_reused_when_rec_and_county_are_given(
        tmp_path):
    """With `rec`/`county` given, classify() DOES perform a real compare (finding 2)
    -- source_url/title agree here, so "manifest matches" is now an honest claim."""
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text(
        "---\nsource_url: https://example.org/a.pdf\ntitle: A County — A Title\n"
        "---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")
    rec = {"url": "https://example.org/a.pdf", "title": "A Title"}
    county = {"name": "A County"}

    result = ingest_counties.classify(out, txt, refetch=False, rec=rec, county=county)

    assert "unchanged" not in result
    assert "manifest matches" in result
    assert "no network" in result


def test_classify_reports_a_manifest_change_as_a_resync_would_happen(tmp_path):
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text(
        "---\nsource_url: https://example.org/OLD.pdf\ntitle: A County — A Title\n"
        "---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")
    rec = {"url": "https://example.org/NEW.pdf", "title": "A Title"}
    county = {"name": "A County"}

    result = ingest_counties.classify(out, txt, refetch=False, rec=rec, county=county)

    assert "manifest changed" in result
    assert "source_url" in result
    assert "no network" in result


def test_classify_reports_an_ocr_document_with_a_manifest_change_as_needing_refetch(
        tmp_path):
    """An OCR'd/stub document's manifest change is never auto-resynced (finding 1's
    anti-fabrication rule applies here too: reconstructing OCR provenance without
    re-running OCR would be a guess dressed as a measurement)."""
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text(
        "---\nsource_url: https://example.org/OLD.pdf\ntitle: A County — A Title\n"
        "text_source: ocr\n---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")
    rec = {"url": "https://example.org/NEW.pdf", "title": "A Title"}
    county = {"name": "A County"}

    result = ingest_counties.classify(out, txt, refetch=False, rec=rec, county=county)

    assert "manifest changed" in result
    assert "--refetch" in result
    assert "not auto-resynced" in result


def test_classify_a_refetch_request_regardless_of_what_is_committed(tmp_path):
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text("---\n---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")

    assert "refetch" in ingest_counties.classify(out, txt, refetch=True)


def test_classify_an_ingested_source_with_no_committed_snapshot_as_needing_a_fetch(tmp_path):
    """A metadata-only OCR stub: the document exists but its text was deliberately
    withheld, so there is nothing here to reuse -- unlike the ordinary case, this
    one still needs the network even without --refetch."""
    out = tmp_path / "stub-doc.md"
    out.write_text("---\n---\n\nbody\n", encoding="utf-8")
    txt = tmp_path / "stub-doc.txt"  # deliberately never created

    result = ingest_counties.classify(out, txt, refetch=False)

    assert "no committed snapshot" in result


# -- write_doc: the real merge wiring, not just the helper in isolation -------------

def test_write_doc_preserves_nonderivable_fields_the_fresh_run_cannot_reproduce(
        tmp_path, monkeypatch):
    """Drives `write_doc()` itself, not `carry_forward_nonderivable()` in isolation --
    the regression lock `tests/test_discover_counties.py` and
    `tests/test_enumerate_cbas.py` both insist on for this exact class of bug: a
    helper that is correct but never wired into the real call site leaves every
    existing test green. Seeds a scratch AGREEMENTS root with a copy of the real
    committed Benton ONA document (edited to also carry a synthetic
    `agency_registry_slugs`, since no real example exists), then re-ingests it with
    a `rec` that has lost its index-recorded `term` and a `text` whose own dates
    this run's own_dates() cannot find -- the shape of the actual bug (#93's
    diff dropped `term`/`effective_date`/`expiry_date`/`union` entirely)."""
    scratch_agreements = tmp_path / "agreements"
    doc_dir = scratch_agreements / "benton-county" / "cba"
    doc_dir.mkdir(parents=True)
    existing_text = REAL_BENTON_DOC.read_text(encoding="utf-8")
    assert "agency_registry_slugs: []" in existing_text
    existing_text = existing_text.replace(
        "agency_registry_slugs: []",
        "agency_registry_slugs: [oregon-health-authority]")
    doc_id = "benton-county-oregon-nurses-association-july-1-2025-june-30-2029"
    (doc_dir / f"{doc_id}.md").write_text(existing_text, encoding="utf-8")

    monkeypatch.setattr(ingest_counties, "AGREEMENTS", scratch_agreements)

    county = {"slug": "benton-county", "name": "Benton County",
              "jurisdiction": "oregon/benton-county"}
    # No "term" key at all -- the county index's own manifest-regeneration lost it
    # (the exact failure mode #93 names). `text` below has no dated span own_dates
    # can find, so eff/exp cannot be re-derived either.
    rec = {"family": "cba", "title": "Oregon Nurses Association (July 1, 2025 – "
                                     "June 30, 2029)",
          "url": "https://hr.bentoncountyor.gov/wp-content/uploads/2026/01/"
                 "ONA%5FBenton%5FCounty%5F25-29-Contract-Final.pdf"}
    text = "This agreement contains no recognizable dated span at all." * 30

    out = ingest_counties.write_doc(county, rec, doc_id, "deadbeef" * 8, 94, text,
                                    "2026-09-12", {}, rec["url"])

    written, _ = ingest_counties.parse_frontmatter(out)
    assert written["union"] == "Oregon Nurses", (
        "union must be preserved when this run cannot re-derive it")
    assert written["term"] == "2025-2029", (
        "term must be carried forward when the index no longer states it and the "
        "text has no matching span -- this is the exact field #93's bug diff dropped")
    assert written["effective_date"] == "2025-07-01"
    assert written["expiry_date"] == "2029-06-30"
    assert written["agency_registry_slugs"] == ["oregon-health-authority"], (
        "a curated agency_registry_slugs value must survive a re-ingest -- this "
        "ingester never derives this field itself")
    assert "public record of a public body" in written["reproduction_basis"]


def test_write_doc_stub_does_not_re_attach_text_derived_dates_from_a_prior_extraction(
        tmp_path, monkeypatch):
    """Finding 1 (code review, fix/safe-reingest): a stub commits no text -- the
    comment at write_doc's own `stub` branch says so ("A stub commits no text, so
    nothing text-derived is trusted: term only as the county's index stated it, no
    dates, no citations"). But `carry_forward_nonderivable(fm, existing)` ran
    unconditionally over ALL of NON_DERIVABLE_FIELDS, including `effective_date` and
    `expiry_date` -- both of which are text-derived (`own_dates()`), never
    index-derived. Reproduced against a scratch copy of the real Benton ONA
    document (which has real effective_date/expiry_date from its original clean
    extraction): re-ingesting it as a stub (the Lane/Marion in-place-overwrite
    failure scenario AGENTS.md names -- a clean source later replaced by an
    image-only scan) must NOT re-assert those dates as read from text this document
    does not hold, and must not assert a term the index no longer states either.
    `union`, `agency_registry_slugs` and `reproduction_basis` are not text-derived
    (index/curation/computed-constant) and MAY still carry forward."""
    scratch_agreements = tmp_path / "agreements"
    doc_dir = scratch_agreements / "benton-county" / "cba"
    doc_dir.mkdir(parents=True)
    existing_text = REAL_BENTON_DOC.read_text(encoding="utf-8")
    assert "agency_registry_slugs: []" in existing_text
    existing_text = existing_text.replace(
        "agency_registry_slugs: []",
        "agency_registry_slugs: [oregon-health-authority]")
    doc_id = "benton-county-oregon-nurses-association-july-1-2025-june-30-2029"
    (doc_dir / f"{doc_id}.md").write_text(existing_text, encoding="utf-8")

    monkeypatch.setattr(ingest_counties, "AGREEMENTS", scratch_agreements)

    county = {"slug": "benton-county", "name": "Benton County",
              "jurisdiction": "oregon/benton-county"}
    # The index no longer states a term either -- the failure scenario is an
    # upstream overwrite, not just an OCR gate failure; nothing about this stub
    # should be able to reconstruct dates from the OLD extraction.
    rec = {"family": "cba", "title": "Oregon Nurses Association (July 1, 2025 – "
                                     "June 30, 2029)",
          "url": "https://hr.bentoncountyor.gov/wp-content/uploads/2026/01/"
                 "ONA%5FBenton%5FCounty%5F25-29-Contract-Final.pdf"}
    stub = {"agreement": 0.32, "figure_agreement": 0.16}

    out = ingest_counties.write_doc(county, rec, doc_id, "deadbeef" * 8, 12, "",
                                    "2026-09-12", {}, rec["url"], stub=stub)

    written, body = ingest_counties.parse_frontmatter(out)
    assert written["effective_date"] == "", (
        "a stub must NEVER re-attach a text-derived effective_date from the "
        "document's PRIOR extraction -- this document holds no text")
    assert written["expiry_date"] == "", (
        "a stub must NEVER re-attach a text-derived expiry_date from the "
        "document's PRIOR extraction -- this document holds no text")
    assert written["term"] == "", (
        "a stub's term is index-only (rec.get('term')); the index no longer "
        "states one here, so it must stay empty, not fall back to the old "
        "extraction's term")
    assert written["union"] == "Oregon Nurses", (
        "union is not text-derived (title-matched); it MAY still carry forward")
    assert written["agency_registry_slugs"] == ["oregon-health-authority"], (
        "agency_registry_slugs is a curation field, not text-derived; it MAY "
        "still carry forward")
    assert "no text is held" in body
    assert "stated in the document's text" not in body, (
        "the glance section must not simultaneously claim dates were stated in "
        "text this document declares it does not hold")


def test_write_doc_does_not_advance_retrieved_when_no_network_was_used(
        tmp_path, monkeypatch):
    """Finding 4 (code review, fix/safe-reingest): write_doc() stamped `retrieved:
    today` unconditionally, and `fetch()` discarded `FETCHER.snapshot`'s `fresh`
    flag (`data, _ = ...`). The 5 committed stub documents have no `.txt`, so the
    main()-level `txt.is_file()` short-circuit never applies to them -- a re-run
    with the source `.pdf` already cached locally advances `retrieved` to today
    having made zero requests. The toolkit provides the exact signal this needs
    (`corpus_toolkit.sources.snapshots.retrieved_date`): `retrieved` may advance
    only when bytes were actually fetched (`fresh=True`); otherwise the committed
    document's own `retrieved` carries forward. Reproduced directly against
    write_doc() with `fresh=False` over a document whose existing `retrieved` is a
    known past date -- the exact "no-.txt path" finding 7 names as untested."""
    scratch_agreements = tmp_path / "agreements"
    doc_dir = scratch_agreements / "benton-county" / "cba"
    doc_dir.mkdir(parents=True)
    existing_text = REAL_BENTON_DOC.read_text(encoding="utf-8")
    assert "retrieved: '2026-08-02'" in existing_text
    doc_id = "benton-county-oregon-nurses-association-july-1-2025-june-30-2029"
    (doc_dir / f"{doc_id}.md").write_text(existing_text, encoding="utf-8")

    monkeypatch.setattr(ingest_counties, "AGREEMENTS", scratch_agreements)

    county = {"slug": "benton-county", "name": "Benton County",
              "jurisdiction": "oregon/benton-county"}
    rec = {"family": "cba", "title": "Oregon Nurses Association (July 1, 2025 – "
                                     "June 30, 2029)",
          "url": "https://hr.bentoncountyor.gov/wp-content/uploads/2026/01/"
                 "ONA%5FBenton%5FCounty%5F25-29-Contract-Final.pdf"}
    text = REAL_BENTON_DOC.read_text(encoding="utf-8")  # any real body text

    out = ingest_counties.write_doc(county, rec, doc_id, "deadbeef" * 8, 94, text,
                                    "2026-09-12", {}, rec["url"], fresh=False)

    written, _ = ingest_counties.parse_frontmatter(out)
    assert written["retrieved"] == "2026-08-02", (
        "no network was used this run (fresh=False) -- retrieved must carry "
        "forward the committed document's own value, not stamp today's date")


def test_write_doc_advances_retrieved_when_a_real_fetch_happened(tmp_path, monkeypatch):
    """The other half of finding 4's fix: `retrieved` must still advance to today
    when this run DID go to the network -- `fresh=True` is the default so a
    genuinely-new ingest (no existing document at all) behaves exactly as before."""
    scratch_agreements = tmp_path / "agreements"
    (scratch_agreements / "benton-county" / "cba").mkdir(parents=True)
    monkeypatch.setattr(ingest_counties, "AGREEMENTS", scratch_agreements)

    county = {"slug": "benton-county", "name": "Benton County",
              "jurisdiction": "oregon/benton-county"}
    doc_id = "benton-county-a-brand-new-document"
    rec = {"family": "cba", "title": "A Brand New Document",
          "url": "https://hr.bentoncountyor.gov/new-document.pdf"}

    out = ingest_counties.write_doc(county, rec, doc_id, "deadbeef" * 8, 5,
                                    "some fresh text " * 20, "2026-09-12", {},
                                    rec["url"], fresh=True)

    written, _ = ingest_counties.parse_frontmatter(out)
    assert written["retrieved"] == "2026-09-12"


# -- main(): the real re-ingest pipeline, no network, byte-identical ---------------

class _NoNetwork:
    """Any network attempt during a plain re-ingest of already-committed documents
    is exactly the bug #93 reports. Raising (rather than e.g. returning canned
    bytes) makes "zero network requests" demonstrable, not asserted."""

    def get(self, url):
        raise AssertionError(f"unexpected network GET during a re-ingest: {url}")

    def snapshot(self, url, dest, refetch=False):
        raise AssertionError(f"unexpected network fetch during a re-ingest: {url}")


def _seed_benton_scratch(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """A scratch copy of the real, already-fully-ingested Benton county group: its
    3 committed documents, their 3 committed `.txt` snapshots, its source manifest
    and the employer registry -- everything `main()` reads for `--only benton`."""
    agreements = tmp_path / "agreements"
    real_cba_dir = REPO_ROOT / "agreements" / "benton-county" / "cba"
    scratch_cba_dir = agreements / "benton-county" / "cba"
    shutil.copytree(real_cba_dir, scratch_cba_dir)

    snapshots = tmp_path / "snapshots"
    snapshots.mkdir()
    for md in scratch_cba_dir.glob("*.md"):
        doc_id = md.stem
        real_txt = REPO_ROOT / "_meta" / "snapshots" / f"{doc_id}.txt"
        shutil.copy(real_txt, snapshots / f"{doc_id}.txt")

    sources_dir = tmp_path / "sources"
    sources_dir.mkdir()
    shutil.copy(REAL_BENTON_SOURCES, sources_dir / "benton.yml")

    employers = tmp_path / "employers.yml"
    shutil.copy(REPO_ROOT / "_meta" / "employers.yml", employers)

    return agreements, snapshots, sources_dir, employers


def _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers):
    monkeypatch.setattr(ingest_counties, "AGREEMENTS", agreements)
    monkeypatch.setattr(ingest_counties, "SNAPSHOTS", snapshots)
    monkeypatch.setattr(ingest_counties, "SOURCES_DIR", sources_dir)
    monkeypatch.setattr(ingest_counties, "EMPLOYERS", employers)
    monkeypatch.setattr(ingest_counties, "REPO_ROOT", agreements.parent)
    monkeypatch.setattr(ingest_counties, "FETCHER", _NoNetwork())


def test_main_reuses_committed_documents_with_zero_network(tmp_path, monkeypatch):
    agreements, snapshots, sources_dir, employers = _seed_benton_scratch(tmp_path)
    _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers)
    before = {p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")}
    monkeypatch.setattr(sys, "argv", ["ingest_counties.py", "--only", "benton"])

    rc = ingest_counties.main()

    assert rc == 0, "a plain re-ingest of already-committed documents must not fail"
    after = {p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")}
    assert after == before, (
        "re-ingesting unchanged documents must produce byte-identical files -- "
        "nothing here should have been rewritten at all")


def test_main_run_twice_over_the_same_committed_documents_is_byte_identical(
        tmp_path, monkeypatch):
    """Acceptance criterion, verbatim: 're-ingesting an unchanged document produces
    a byte-identical file: run it twice over a sample and show an empty diff.'"""
    agreements, snapshots, sources_dir, employers = _seed_benton_scratch(tmp_path)
    _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers)
    monkeypatch.setattr(sys, "argv", ["ingest_counties.py", "--only", "benton"])

    assert ingest_counties.main() == 0
    first_run = {p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")}
    assert ingest_counties.main() == 0
    second_run = {p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")}

    assert first_run == second_run


def test_main_check_mode_touches_no_file_and_no_network(tmp_path, monkeypatch, capsys):
    agreements, snapshots, sources_dir, employers = _seed_benton_scratch(tmp_path)
    _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers)
    before = {p: p.stat().st_mtime_ns
             for p in (agreements / "benton-county" / "cba").glob("*.md")}
    monkeypatch.setattr(sys, "argv", ["ingest_counties.py", "--only", "benton", "--check"])

    rc = ingest_counties.main()

    assert rc == 0
    after = {p: p.stat().st_mtime_ns
            for p in (agreements / "benton-county" / "cba").glob("*.md")}
    assert after == before, "--check must not write anything, not even a re-write to the same bytes"
    out = capsys.readouterr().out
    # Finding 3 (code review, fix/safe-reingest): "unchanged" is DRIFT.md's word for a
    # measured hash compare, which this ingester never performs (that is
    # corpus-detect-changes's job -- see AGENTS.md's "Explicitly NOT a finding"). All
    # 3 Benton sources DO now get a real compare (manifest url/title vs. the committed
    # document -- finding 2's fix), and all 3 agree, so the honest claim is "manifest
    # matches", never "unchanged".
    assert "unchanged" not in out
    assert out.count("reused — manifest matches, no network") == 3, (
        "all 3 already-ingested Benton documents, whose manifest still matches what "
        "is committed, should report as reusable")


# -- finding 2: a changed manifest (source_url/title) must reach the committed ------
# -- document with NO network when the extraction is already cached ---------------

def _mutate_benton_ona_url(sources_dir: Path, new_url: str) -> None:
    """Simulates exactly what the reviewer did to reproduce finding 2: the county
    re-posts the same document at a new URL (or `discover_counties.py` regenerates
    the manifest against a moved index) and `_meta/sources/benton.yml` picks it up
    with NO re-ingest having happened yet."""
    path = sources_dir / "benton.yml"
    group = yaml.safe_load(path.read_text(encoding="utf-8"))
    for src in group["sources"]:
        if src["id"].endswith("oregon-nurses-association-july-1-2025-june-30-2029"):
            src["url"] = new_url
    path.write_text(yaml.safe_dump(group, sort_keys=False), encoding="utf-8")


def test_main_propagates_a_changed_manifest_url_with_zero_network(tmp_path, monkeypatch):
    """Finding 2 (code review, fix/safe-reingest): the reuse short-circuit
    (`out.is_file() and txt.is_file()`) never compared the manifest record against
    the committed document, so a source re-posted at a new URL kept the stale
    `source_url` forever -- reproduced by the reviewer by rewriting `url` in
    `_meta/sources/benton.yml` and re-ingesting: "reused 3 unchanged, no network",
    document rewritten NONE, stale `source_url` kept. The fix compares the fresh
    manifest against the committed frontmatter with no network at all, and when it
    finds a difference, resyncs the document from the CACHED `.txt` (still zero
    network) rather than silently keeping the stale value or requiring --refetch."""
    agreements, snapshots, sources_dir, employers = _seed_benton_scratch(tmp_path)
    doc_id = "benton-county-oregon-nurses-association-july-1-2025-june-30-2029"
    # A raw snapshot must be cached locally for the no-network resync to have bytes
    # to hash (`hash_snapshot` always reads the raw file) -- its CONTENT is
    # irrelevant here because the committed .txt is long enough that hash_snapshot
    # never falls back to it.
    (snapshots / f"{doc_id}.pdf").write_bytes(b"stand-in cached raw bytes for the test")
    new_url = ("https://hr.bentoncountyor.gov/wp-content/uploads/2027/01/"
              "ONA-Benton-County-25-29-Contract-REPOSTED.pdf")
    _mutate_benton_ona_url(sources_dir, new_url)
    _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers)
    other_docs_before = {
        p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")
        if p.stem != doc_id}
    monkeypatch.setattr(sys, "argv", ["ingest_counties.py", "--only", "benton"])

    rc = ingest_counties.main()

    assert rc == 0, "a no-network manifest resync must not fail"
    written, _ = ingest_counties.parse_frontmatter(
        agreements / "benton-county" / "cba" / f"{doc_id}.md")
    assert written["source_url"] == new_url, (
        "the changed manifest url must propagate to the committed document with "
        "no network -- this is the exact field finding 2's reproduction showed "
        "stuck at its stale value forever")
    assert written["union"] == "Oregon Nurses", "unrelated fields must not be lost"
    assert written["term"] == "2025-2029"
    other_docs_after = {
        p: p.read_bytes() for p in (agreements / "benton-county" / "cba").glob("*.md")
        if p.stem != doc_id}
    assert other_docs_after == other_docs_before, (
        "the two Benton sources whose manifest did NOT change must stay untouched")


def test_main_declines_to_resync_a_manifest_change_with_no_cached_raw_snapshot(
        tmp_path, monkeypatch):
    """The safety half of finding 2's fix: when the manifest changed but there is no
    cached raw snapshot to resync from (a fresh worktree, per #93's own measurement
    of 283 cached vs. 10 in a fresh checkout), the ingester must decline rather than
    fabricate a document from nothing or silently keep the stale value -- AGENTS.md's
    overriding rule, "could not check is never reported as is not there", cuts the
    other way here too: a resync it cannot safely perform is reported as needing
    --refetch, not silently skipped as if nothing changed."""
    agreements, snapshots, sources_dir, employers = _seed_benton_scratch(tmp_path)
    doc_id = "benton-county-oregon-nurses-association-july-1-2025-june-30-2029"
    new_url = "https://hr.bentoncountyor.gov/wp-content/uploads/2027/01/reposted.pdf"
    _mutate_benton_ona_url(sources_dir, new_url)
    _patch_paths(monkeypatch, agreements, snapshots, sources_dir, employers)
    before = (agreements / "benton-county" / "cba" / f"{doc_id}.md").read_bytes()
    monkeypatch.setattr(sys, "argv", ["ingest_counties.py", "--only", "benton"])

    rc = ingest_counties.main()

    assert rc == 0, "declining a resync is not a failure"
    after = (agreements / "benton-county" / "cba" / f"{doc_id}.md").read_bytes()
    assert after == before, (
        "with no cached raw snapshot, the document must not be rewritten at all -- "
        "neither with the stale url nor with a fabricated resync")
