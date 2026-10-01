"""oregon-collective-bargaining#100: the Curator notes sentence about a state CBA's
predecessor must say what is actually true for THAT document -- derived from its own
`relationships.supersedes` -- instead of a static claim ("planned for the history
tranche") that the history tranche's own completion made false everywhere.

`supersedes_note()` is the single place that sentence is built, so `write_doc()`
(write time, supersedes always empty), `link_supersedes()` and `retire_blackline()`
(which add `supersedes` AFTER the body is written) all render the same truth from
the same frontmatter field, and the sentence cannot go stale the way a hardcoded
string already did once.
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


# ---------------------------------------------------------------------------
# supersedes_note(): the sentence builder itself
# ---------------------------------------------------------------------------

def test_note_says_linked_and_names_the_id_when_supersedes_is_set():
    note = ingest_cbas.supersedes_note(["state-foo-union-2021-2023"])
    assert "`state-foo-union-2021-2023`" in note
    assert "relationships.supersedes" in note
    assert "planned for the" not in note
    assert "history tranche" not in note or "ingested in the history tranche" in note


def test_note_names_every_id_when_more_than_one():
    note = ingest_cbas.supersedes_note(["state-a-2021-2023", "state-b-2023-2025"])
    assert "`state-a-2021-2023`" in note
    assert "`state-b-2023-2025`" in note


def test_note_says_not_ingested_when_supersedes_is_empty():
    note = ingest_cbas.supersedes_note([])
    assert "not ingested" in note or "No predecessor" in note
    assert "relationships.supersedes" not in note
    assert "planned for the" not in note


# ---------------------------------------------------------------------------
# refresh_supersedes_note(): rewrites an on-disk document's sentence from its
# OWN current frontmatter -- what link_supersedes() and retire_blackline() must
# call after they add `supersedes`.
# ---------------------------------------------------------------------------

def _write_doc(path: Path, supersedes: list[str]) -> None:
    fm = {
        "id": "state-x-2023-2025",
        "relationships": {"implements": [], "implemented_by": [],
                          "references_external": [], "related": [],
                          "supersedes": supersedes},
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
    _write_doc(p, ["state-x-2021-2023"])
    assert ingest_cbas.refresh_supersedes_note(p) is True
    _, body = _fm_and_body(p)
    assert "`state-x-2021-2023`" in body
    assert "planned for the" not in body


def test_refresh_is_idempotent(tmp_path):
    p = tmp_path / "doc.md"
    _write_doc(p, [])
    assert ingest_cbas.refresh_supersedes_note(p) is True
    assert ingest_cbas.refresh_supersedes_note(p) is False


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
        supersedes = fm.get("relationships", {}).get("supersedes") or []
        says_linked = "linked in `relationships.supersedes`" in body
        says_not_ingested = "No predecessor term's agreement is ingested" in body
        if supersedes:
            if not says_linked:
                mismatched.append((path.name, "has supersedes but sentence doesn't"))
            for sid in supersedes:
                if f"`{sid}`" not in body:
                    mismatched.append((path.name, f"missing id {sid}"))
        else:
            if not says_not_ingested:
                mismatched.append((path.name, "has no supersedes but doesn't say so"))
    assert mismatched == []
