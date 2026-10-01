"""`src/ingest_marion_successors.py` -- the targeted frontmatter edits used to land
Marion's MCDAA 2026-2029 and MCJEA 2026-2028 successor agreements
(oregon-collective-bargaining#63).

THE SEAM: these are the same "targeted line edit, never a YAML re-dump" functions
`src/anchor_sections.py` already uses (`set_field`) -- hand formatting must survive
both on the brand-new successor document (stamping `relationships.supersedes`) and
on the predecessor that stays committed (flipping `status: current` to
`status: superseded` without touching its text, hash, or `retrieved`).

Driven against the REAL committed Marion documents (same seam decision as
`tests/test_ingest_counties.py`: real fixtures, not hand-authored YAML snippets),
so a regex that happens to work on a synthetic sample but not on this corpus's
actual quoting/spacing is caught here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import ingest_marion_successors as ims  # noqa: E402

MCDAA = REPO_ROOT / "agreements" / "marion-county" / "cba" / "marion-county-mcdaa-cba.md"
MCJEA = REPO_ROOT / "agreements" / "marion-county" / "cba" / "marion-county-mcjea-cba.md"


# -- set_supersedes ---------------------------------------------------------------

def test_set_supersedes_fills_an_empty_list():
    text = MCDAA.read_text(encoding="utf-8")
    assert "  supersedes: []" in text

    out = ims.set_supersedes(text, ["marion-county-mcdaa-cba"])

    assert "  supersedes: []" not in out
    assert "  supersedes:\n  - marion-county-mcdaa-cba\n" in out
    # Nothing else in the frontmatter or body moved -- a targeted edit, not a re-dump.
    assert out.replace("  supersedes:\n  - marion-county-mcdaa-cba\n", "  supersedes: []\n") == text


def test_set_supersedes_is_idempotent_and_sorts():
    text = MCDAA.read_text(encoding="utf-8")
    once = ims.set_supersedes(text, ["marion-county-mcdaa-cba"])
    twice = ims.set_supersedes(once, ["marion-county-mcdaa-cba"])
    assert once == twice


def test_set_supersedes_with_multiple_ids_is_sorted():
    text = MCDAA.read_text(encoding="utf-8")
    out = ims.set_supersedes(text, ["zzz-later-id", "aaa-earlier-id"])
    assert "  supersedes:\n  - aaa-earlier-id\n  - zzz-later-id\n" in out


def test_set_supersedes_raises_when_field_absent():
    with pytest.raises(ValueError):
        ims.set_supersedes("no frontmatter field here", ["x"])


# -- flip_status --------------------------------------------------------------

def test_flip_status_to_superseded_touches_only_that_line():
    # Synthetic text, not the live MCDAA fixture: this repo's own successor
    # ingestion (oregon-collective-bargaining#63) already flips the real
    # committed MCDAA/MCJEA documents to `status: superseded`, so a `status:
    # current` fixture must not be assumed to still be on disk.
    text = "---\nid: x\nstatus: current\nother: y\n---\n\nbody\n"

    out = ims.flip_status(text, "superseded")

    assert "\nstatus: superseded\n" in out
    assert out.replace("\nstatus: superseded\n", "\nstatus: current\n", 1) == text


def test_flip_status_does_not_touch_source_sha256_or_full_text():
    text = MCJEA.read_text(encoding="utf-8")
    out = ims.flip_status(text, "superseded")
    for field in ("source_sha256:", "retrieved:", "## Full text"):
        before = text[text.index(field):text.index(field) + 60]
        after = out[out.index(field):out.index(field) + 60]
        assert before == after


def test_flip_status_raises_when_field_absent():
    with pytest.raises(ValueError):
        ims.flip_status("no status field here", "superseded")


# -- add_supersession_note -----------------------------------------------------

def test_add_supersession_note_appears_right_after_the_curator_notes_heading():
    text = MCDAA.read_text(encoding="utf-8")
    note = "Superseded by `marion-county-mcdaa-cba-2026-2029` (2026-2029 term)."

    out = ims.add_supersession_note(text, note)

    assert note in out
    heading = "## Curator notes\n\n"
    assert out.index(heading) + len(heading) == out.index(note)
    # The rest of the Curator notes prose still follows, untouched.
    assert "This document is `content_mode: verbatim`" in out


def test_add_supersession_note_raises_when_heading_absent():
    with pytest.raises(ValueError):
        ims.add_supersession_note("no curator heading here", "note")


# -- fix_class_note_for_superseded / fix_class_note_for_successor (finding 1, 4) --

def test_fix_class_note_for_superseded_drops_the_status_current_claim():
    # The committed MCDAA predecessor is already `status: superseded` and already
    # carries the fixed class note (this PR's own correction), so a synthetic
    # fixture stands in for a document still carrying the stale boilerplate.
    text = (
        "Summary-first is the recorded class determination (`corpus.yml\n"
        "schema.doc_types`, `verbatim: false`). `status: current` records that this\n"
        "document sits on the county's own operative labor-agreements index at ingest\n"
        "time — county pages, unlike the DAS library, publish no history, so currency\n"
        "rests on the index and on content-hash drift detection.\n"
        "Extraction: pdftotext -layout.\n")

    out = ims.fix_class_note_for_superseded(text, "marion-county-mcdaa-cba-2026-2029")

    assert "status: current" not in out
    assert "verbatim: false" not in out
    assert "marion-county-mcdaa-cba-2026-2029" in out
    assert "Extraction: pdftotext -layout." in out   # untouched trailing line


def test_fix_class_note_for_superseded_is_idempotent():
    text = MCDAA.read_text(encoding="utf-8")
    once = ims.fix_class_note_for_superseded(text, "marion-county-mcdaa-cba-2026-2029")
    twice = ims.fix_class_note_for_superseded(once, "marion-county-mcdaa-cba-2026-2029")
    assert once == twice == text   # already fixed on disk — a true no-op


def test_fix_class_note_for_successor_raises_when_boilerplate_absent():
    with pytest.raises(ValueError):
        ims.fix_class_note_for_successor("no boilerplate here", "2026-10-01")


# -- reword_index_claim (finding 1) --------------------------------------------

def test_reword_index_claim_drops_the_false_index_listing():
    text = (REPO_ROOT / "agreements" / "marion-county" / "cba"
           / "marion-county-mcdaa-cba-2026-2029.md").read_text(encoding="utf-8")
    assert "Listed on the county's labor agreements index as" not in text  # already fixed

    synthetic = ('- Listed on the county\'s labor agreements index as: '
                '“MCDAA CBA (2026-2029)” (index archived in `_meta/discovery/`)\n'
                '- Source document: 51 pages (PDF)\n')
    out = ims.reword_index_claim(synthetic, "2026-10-01")
    assert "Listed on the county's labor agreements index as" not in out
    assert "Identified as the successor from the PDF's own text" in out
    assert "- Source document: 51 pages (PDF)" in out   # untouched following line


def test_reword_index_claim_raises_when_bullet_absent():
    with pytest.raises(ValueError):
        ims.reword_index_claim("no such bullet here", "2026-10-01")


# -- set_expiry_date / add_expiry_glance_line (finding 3) -----------------------

def test_set_expiry_date_fills_an_empty_field():
    text = "---\nid: x\nexpiry_date: ''\nother: y\n---\n\nbody\n"
    out = ims.set_expiry_date(text, "2029-06-30")
    assert "expiry_date: '2029-06-30'" in out
    assert out.replace("expiry_date: '2029-06-30'", "expiry_date: ''") == text


def test_set_expiry_date_raises_when_field_already_filled_or_absent():
    with pytest.raises(ValueError):
        ims.set_expiry_date("expiry_date: '2020-01-01'\n", "2029-06-30")
    with pytest.raises(ValueError):
        ims.set_expiry_date("no such field\n", "2029-06-30")


def test_add_expiry_glance_line_inserts_right_before_source_document():
    text = "- Some other bullet\n- Source document: 51 pages (PDF)\n"
    out = ims.add_expiry_glance_line(text, "2029-06-30")
    assert "- Expiry stated in the document's text: 2029-06-30\n- Source document:" in out


def test_add_expiry_glance_line_raises_when_marker_absent():
    with pytest.raises(ValueError):
        ims.add_expiry_glance_line("no source-document bullet here", "2029-06-30")


# -- supersede_predecessor (finding 4: independently idempotent pieces) --------

def test_supersede_predecessor_is_a_no_op_once_fully_applied(tmp_path, monkeypatch):
    # The real committed MCDAA predecessor already has `status: superseded`, the
    # supersession note, and the fixed class note (this PR's own corrections) --
    # a re-run against it must report nothing changed and write nothing.
    fixture = tmp_path / "marion-county-mcdaa-cba.md"
    fixture.write_text(MCDAA.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(ims, "AGREEMENTS", tmp_path)

    changed = ims.supersede_predecessor(
        "marion-county-mcdaa-cba", "marion-county-mcdaa-cba-2026-2029", "2026-2029")

    assert changed is False
    assert fixture.read_text(encoding="utf-8") == MCDAA.read_text(encoding="utf-8")


def test_supersede_predecessor_fixes_a_status_flip_left_from_before_this_fix_existed(
        tmp_path, monkeypatch):
    # Simulates the real state the branch was in before finding 4's fix: `status`
    # already flipped and the note already inserted, but the class note still the
    # stale, now-contradictory boilerplate.
    text = MCDAA.read_text(encoding="utf-8")
    stale = text.replace(
        "This document is `content_mode: verbatim` per the class determination in "
        "`corpus.yml schema.doc_types` (`verbatim: true`). `status: superseded` "
        "records that the stable URL above now serves "
        "`marion-county-mcdaa-cba-2026-2029`'s text; this document's own text, hash, "
        "and `retrieved` date are frozen as committed and are not re-fetched.",
        "Summary-first is the recorded class determination (`corpus.yml\n"
        "schema.doc_types`, `verbatim: false`). `status: current` records that this\n"
        "document sits on the county's own operative labor-agreements index at ingest\n"
        "time — county pages, unlike the DAS library, publish no history, so currency\n"
        "rests on the index and on content-hash drift detection.")
    assert stale != text   # the replacement above actually matched something
    fixture = tmp_path / "marion-county-mcdaa-cba.md"
    fixture.write_text(stale, encoding="utf-8")
    monkeypatch.setattr(ims, "AGREEMENTS", tmp_path)

    changed = ims.supersede_predecessor(
        "marion-county-mcdaa-cba", "marion-county-mcdaa-cba-2026-2029", "2026-2029")

    assert changed is True
    out = fixture.read_text(encoding="utf-8")
    assert "status: current" not in out
    assert "status: superseded" in out
    # The status flip itself was already done and must not be duplicated.
    assert out.count("**Superseded by `marion-county-mcdaa-cba-2026-2029`**") == 1
