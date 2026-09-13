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


# -- classify (the --check seam) -----------------------------------------------------

def test_classify_a_never_ingested_source_as_new(tmp_path):
    out = tmp_path / "new-doc.md"
    txt = tmp_path / "new-doc.txt"
    assert "new" in ingest_counties.classify(out, txt, refetch=False)


def test_classify_an_ingested_source_with_a_committed_snapshot_as_unchanged(tmp_path):
    out = tmp_path / "doc.md"
    txt = tmp_path / "doc.txt"
    out.write_text("---\n---\n\nbody\n", encoding="utf-8")
    txt.write_text("some extracted text " * 20, encoding="utf-8")

    result = ingest_counties.classify(out, txt, refetch=False)

    assert "unchanged" in result
    assert "no network" in result


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


# -- main(): the real re-ingest pipeline, no network, byte-identical ---------------

class _NoNetwork:
    """Any network attempt during a plain re-ingest of already-committed documents
    is exactly the bug #93 reports. Raising (rather than e.g. returning canned
    bytes) makes "zero network requests" demonstrable, not asserted."""

    def get(self, url):
        raise AssertionError(f"unexpected network GET during a re-ingest: {url}")

    def snapshot(self, url, dest, refetch=False):
        raise AssertionError(f"unexpected network fetch during a re-ingest: {url}")


def _seed_benton_scratch(tmp_path: Path) -> tuple[Path, Path, Path]:
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
    assert out.count("unchanged — committed snapshot reused, no network") == 3, (
        "all 3 already-ingested Benton documents should report as reusable/unchanged")
