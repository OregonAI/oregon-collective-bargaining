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
    text = MCDAA.read_text(encoding="utf-8")
    assert "\nstatus: current\n" in text

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
    assert "Summary-first is the recorded class determination" in out


def test_add_supersession_note_raises_when_heading_absent():
    with pytest.raises(ValueError):
        ims.add_supersession_note("no curator heading here", "note")
