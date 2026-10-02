"""oregon-collective-bargaining#100: the Curator notes sentence about a state CBA's
predecessor must say what is actually true for THAT document -- derived from its own
`status`, `relationships.supersedes` and `relationships.related` -- instead of a
static claim ("planned for the history tranche") that the history tranche's own
completion made false everywhere.

`supersedes_note()` is the single place that sentence is built, so `write_doc()`
(write time, supersedes always empty), `link_supersedes()` and `retire_blackline()`
(which add `supersedes`/`related` AFTER the body is written) all render the same
truth from the same frontmatter fields, and the sentence cannot go stale the way a
hardcoded string already did once.

Two more things the first pass at this got wrong, both covered below:
  * "no predecessor is ingested ... a recorded decision" is true ONLY for
    `superseded` documents (the permanent deep-archive case). A `current` document
    whose immediate predecessor exists in the manifest but was never paired is an
    oversight, not a decision, and must say so instead.
  * the blackline case: `supersedes` empty does not always mean no predecessor is
    ingested -- link_supersedes() puts a draft's predecessor under `related`
    instead (a draft supersedes nothing), and the sentence must say THAT, not
    "no predecessor is ingested".
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import ingest_cbas  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CBA_DIR = ROOT / "agreements" / "state" / "cba"


def _fm_and_body(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    _, fm_text, body = text.split("---\n", 2)
    return yaml.safe_load(fm_text), body


def _rel(supersedes=(), related=()) -> dict:
    return {"implements": [], "implemented_by": [], "references_external": [],
            "related": list(related), "supersedes": list(supersedes)}


def _flat(text: str) -> str:
    """Collapse the word-wrapped newlines so a phrase spanning a wrap point
    (e.g. "recorded\\ndecision") can still be matched as one phrase."""
    return " ".join(text.split())


# ---------------------------------------------------------------------------
# supersedes_note(): the sentence builder itself
# ---------------------------------------------------------------------------

def test_note_says_linked_and_names_the_id_when_supersedes_is_set():
    note = ingest_cbas.supersedes_note(
        "current", _rel(supersedes=["state-foo-union-2021-2023"]))
    assert "`state-foo-union-2021-2023`" in note
    assert "relationships.supersedes" in note
    assert "planned for the" not in note
    # retire_blackline() also fills `supersedes` outside the history tranche, so
    # the sentence must not claim tranche provenance it cannot prove.
    assert "history tranche" not in note


def test_note_names_every_id_when_more_than_one():
    note = ingest_cbas.supersedes_note(
        "current", _rel(supersedes=["state-a-2021-2023", "state-b-2023-2025"]))
    assert "`state-a-2021-2023`" in note
    assert "`state-b-2023-2025`" in note


def test_note_says_recorded_decision_only_for_superseded_with_nothing_linked():
    note = _flat(ingest_cbas.supersedes_note("superseded", _rel()))
    assert "No predecessor" in note
    assert "recorded decision" in note
    assert "relationships.supersedes" not in note
    assert "planned for the" not in note


def test_note_says_pairing_gap_not_recorded_decision_for_current_with_nothing_linked():
    # The 3 renamed-unit documents: an immediate predecessor exists in the
    # manifest but was never paired. This must NOT borrow the archive's
    # "recorded decision" wording -- that would repeat the same false claim
    # issue #100 reported, just with a different label.
    note = _flat(ingest_cbas.supersedes_note("current", _rel()))
    assert "No predecessor" in note or "not" in note
    assert "recorded decision" not in note
    assert "pairing" in note


def test_note_says_linked_in_related_for_the_draft_blackline_case():
    # A draft supersedes nothing -- link_supersedes() puts the predecessor
    # under `related` instead of `supersedes`. The sentence must say the
    # predecessor IS ingested and name where it's linked, not "no predecessor
    # is ingested".
    note = ingest_cbas.supersedes_note(
        "superseded", _rel(related=["state-seiu-master-agreement-"
                                    "collective-bargaining-agreement-2023-2025"]))
    assert "ingested" in note
    assert "`state-seiu-master-agreement-collective-bargaining-agreement-2023-2025`" in note
    assert "relationships.related" in note
    assert "No predecessor" not in note


def test_supersedes_takes_priority_over_related_when_both_are_set():
    note = ingest_cbas.supersedes_note(
        "current", _rel(supersedes=["state-a-2023-2025"], related=["state-b-2023-2025"]))
    assert "`state-a-2023-2025`" in note
    assert "relationships.supersedes" in note
    assert "relationships.related" not in note


# ---------------------------------------------------------------------------
# refresh_supersedes_note(): rewrites an on-disk document's sentence from its
# OWN current frontmatter -- what link_supersedes() and retire_blackline() must
# call after they add `supersedes`/`related`.
# ---------------------------------------------------------------------------

def _write_doc(path: Path, status: str, supersedes: list[str] = (),
              related: list[str] = ()) -> None:
    fm = {
        "id": "state-x-2023-2025",
        "status": status,
        "relationships": _rel(supersedes=supersedes, related=related),
    }
    body = ("\n## Curator notes\n\nLetters of agreement bound into this PDF by DAS "
            "are part of this source\nsnapshot; separately-published LOAs are their "
            "own documents in a later tranche.\nThe predecessor term's agreement is "
            "in the DAS library and is planned for the\nhistory tranche — "
            "`supersedes` is recorded then, not faked now.\n\n"
            "Extraction: pdftotext -layout; 1 page, 10 characters extracted; "
            "NOT human-verified.\n")
    path.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n" + body,
                    encoding="utf-8")


def test_refresh_rewrites_the_stale_sentence_to_match_frontmatter(tmp_path):
    p = tmp_path / "doc.md"
    _write_doc(p, "current", supersedes=["state-x-2021-2023"])
    assert ingest_cbas.refresh_supersedes_note(p) is True
    _, body = _fm_and_body(p)
    assert "`state-x-2021-2023`" in body
    assert "planned for the" not in body


def test_refresh_is_idempotent(tmp_path):
    p = tmp_path / "doc.md"
    _write_doc(p, "superseded")
    assert ingest_cbas.refresh_supersedes_note(p) is True
    assert ingest_cbas.refresh_supersedes_note(p) is False


def test_refresh_uses_related_for_a_superseded_blackline(tmp_path):
    p = tmp_path / "doc.md"
    _write_doc(p, "superseded", related=["state-seiu-master-2023-2025"])
    assert ingest_cbas.refresh_supersedes_note(p) is True
    _, body = _fm_and_body(p)
    assert "`state-seiu-master-2023-2025`" in body
    assert "No predecessor term's agreement is ingested" not in body


# ---------------------------------------------------------------------------
# link_supersedes() must refresh the sentence on the document it just linked --
# it adds `relationships.supersedes` AFTER the body was written at a time the
# predecessor did not exist yet.
# ---------------------------------------------------------------------------

def test_link_supersedes_refreshes_the_linked_documents_sentence(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_cbas, "OUT_DIR", tmp_path)
    roster = {"state_contracts": [{"match": "Unit X", "unit": "Unit X"}],
             "non_state_contracts": []}
    cur = tmp_path / "state-x-2025-2027.md"
    pred = tmp_path / "state-x-2023-2025.md"
    for p, status, doc_id in ((cur, "current", "state-x-2025-2027"),
                              (pred, "superseded", "state-x-2023-2025")):
        fm = {"id": doc_id, "title": "Unit X Agreement", "status": status,
              "relationships": {"implements": [], "implemented_by": [],
                                "references_external": [], "related": [],
                                "supersedes": []}}
        p.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n"
                     + "\nLetters of agreement bound into this PDF by DAS are part "
                       "of this source\nsnapshot; separately-published LOAs are "
                       "their own documents in a later tranche.\nThe predecessor "
                       "term's agreement is in the DAS library and is planned for "
                       "the\nhistory tranche — `supersedes` is recorded then, not "
                       "faked now.\n\nExtraction: pdftotext -layout; 1 page, 10 "
                       "characters extracted; NOT human-verified.\n", encoding="utf-8")

    linked = ingest_cbas.link_supersedes(roster, {"state-x-2023-2025"})
    assert linked == 1
    body = cur.read_text(encoding="utf-8")
    assert "`state-x-2023-2025`" in body
    assert "planned for the" not in body


# ---------------------------------------------------------------------------
# Corpus-wide gate: every existing state CBA's sentence agrees with its own
# frontmatter, and the old stale sentence appears nowhere.
# ---------------------------------------------------------------------------

def test_no_state_cba_carries_the_stale_sentence():
    stale = [p.name for p in CBA_DIR.glob("*.md")
             if "planned for the" in p.read_text(encoding="utf-8")
             and "history tranche" in p.read_text(encoding="utf-8")]
    assert stale == []


def test_every_state_cba_sentence_agrees_with_its_own_supersedes():
    mismatched = []
    for path in sorted(CBA_DIR.glob("*.md")):
        fm, body = _fm_and_body(path)
        flat = _flat(body)
        rel = fm.get("relationships", {})
        supersedes = rel.get("supersedes") or []
        related = rel.get("related") or []
        says_linked = "linked in `relationships.supersedes`" in flat
        says_linked_related = "linked in `relationships.related`" in flat
        says_not_ingested = "No predecessor term's agreement is ingested" in flat
        says_not_linked_yet = "No predecessor term's agreement is linked" in flat
        if supersedes:
            if not says_linked:
                mismatched.append((path.name, "has supersedes but sentence doesn't"))
            for sid in supersedes:
                if f"`{sid}`" not in flat:
                    mismatched.append((path.name, f"missing id {sid}"))
            if "recorded decision" in flat:
                mismatched.append((path.name, "has supersedes but claims 'recorded "
                                               "decision' (that's the empty case)"))
        elif related:
            if not says_linked_related:
                mismatched.append((path.name, "has related but sentence doesn't say so"))
            for rid in related:
                if f"`{rid}`" not in flat:
                    mismatched.append((path.name, f"missing related id {rid}"))
            if says_not_ingested:
                mismatched.append((path.name, "has related predecessor but still "
                                               "claims no predecessor is ingested"))
        else:
            if not (says_not_ingested or says_not_linked_yet):
                mismatched.append((path.name, "has no supersedes/related but doesn't "
                                               "say so"))
            # "recorded decision" wording is only true of the permanent deep-archive
            # case, which only applies to `superseded` documents.
            if "recorded decision" in flat and fm.get("status") != "superseded":
                mismatched.append((path.name, "claims 'recorded decision' but status "
                                               f"is {fm.get('status')!r}, not "
                                               "'superseded'"))
    assert mismatched == []
