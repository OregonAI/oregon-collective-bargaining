"""oregon-collective-bargaining#104: three 2025-2027 roster rows were renamed to
the current-term title wording and their `match` string no longer matches the
2023-2025 predecessor's older title in `_meta/sources/state.yml`, so
`history_picks()`/`link_supersedes()` silently skip that predecessor (see KNOWN
GAPS in `src/ingest_cbas.py`'s docstring, prior to this fix).

The explicit-id-override option named in that docstring is implemented as an
optional `predecessor_match` roster-row key: `matches_row()` pairs a title
against EITHER `match` (the current-term title) OR `predecessor_match` (the
older predecessor title), so the roster row still names exactly one unit on
one line, with no change to how `match` governs the current document.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import ingest_cbas  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROSTER_FILE = ROOT / "_meta" / "state-roster-2025-2027.yml"


def test_matches_row_still_matches_the_current_title_via_match():
    row = {"match": "AFSCME Oregon Emergency Management",
           "predecessor_match": "AFSCME Oregon Department of Emergency Management"}
    assert ingest_cbas.matches_row(row, "AFSCME Oregon Emergency Management 2025-2027")


def test_matches_row_matches_the_older_predecessor_title_via_predecessor_match():
    row = {"match": "AFSCME Oregon Emergency Management",
           "predecessor_match": "AFSCME Oregon Department of Emergency Management"}
    assert ingest_cbas.matches_row(
        row, "AFSCME Oregon Department of Emergency Management 2023-2025")


def test_matches_row_without_predecessor_match_is_unaffected():
    row = {"match": "AFSCME Oregon Emergency Management"}
    assert not ingest_cbas.matches_row(
        row, "AFSCME Oregon Department of Emergency Management 2023-2025")


def test_history_picks_only_filters_to_the_given_ids():
    group = {"sources": [
        {"id": "state-x-2023-2025", "family": "cba", "term": "2023-2025",
         "title": "Unit X 2023-2025"},
        {"id": "state-y-2023-2025", "family": "cba", "term": "2023-2025",
         "title": "Unit Y 2023-2025"},
    ]}
    roster = {"state_contracts": [
        {"unit": "Unit X", "match": "Unit X"},
        {"unit": "Unit Y", "match": "Unit Y"},
    ], "non_state_contracts": []}
    picked = ingest_cbas.history_picks(group, roster, "2025", only={"state-x-2023-2025"})
    assert [r["id"] for r in picked] == ["state-x-2023-2025"]


def test_history_picks_finds_a_predecessor_whose_title_only_matches_predecessor_match():
    """The #104 behaviour itself: a renamed unit's roster row whose `match` is the
    current-term title must still pick up its predecessor via `predecessor_match` --
    not just report that `matches_row()` returns True for it in isolation."""
    group = {"sources": [
        {"id": "state-unit-x-old-2023-2025", "family": "cba", "term": "2023-2025",
         "title": "Unit X Old 2023-2025"},
        {"id": "state-unit-x-new-2025-2027", "family": "cba", "term": "2025-2027",
         "title": "Unit X New 2025-2027"},
    ]}
    roster = {"state_contracts": [
        {"unit": "Unit X", "match": "Unit X New", "predecessor_match": "Unit X Old"},
    ], "non_state_contracts": []}
    picked = ingest_cbas.history_picks(group, roster, "2025")
    assert [r["id"] for r in picked] == ["state-unit-x-old-2023-2025"]


def test_roster_row_finds_the_chart_row_for_a_predecessor_title_via_predecessor_match():
    roster = {"state_contracts": [
        {"unit": "AFSCME OEM Dept. of Emergency Management", "repr": "AV",
         "match": "AFSCME Oregon Emergency Management",
         "predecessor_match": "AFSCME Oregon Department of Emergency Management"},
    ], "non_state_contracts": []}
    row = ingest_cbas.roster_row(
        "AFSCME Oregon Department of Emergency Management 2023-2025", roster)
    assert row is not None
    assert row["unit"] == "AFSCME OEM Dept. of Emergency Management"


def test_roster_carries_predecessor_match_for_the_three_renamed_units():
    roster = yaml.safe_load(ROSTER_FILE.read_text(encoding="utf-8"))
    by_unit = {r["unit"]: r for r in roster["state_contracts"] + roster["non_state_contracts"]}
    expectations = {
        "AFSCME OEM Dept. of Emergency Management":
            "AFSCME Oregon Department of Emergency Management",
        "AFSCME OLTCO Long Term Care Ombudsman":
            "AFSCME Office of the Long Term Care Ombudsman",
        "IAFF PANG Local 1660": "IAFF Portland Air National Guard",
    }
    for unit, predecessor_title_substring in expectations.items():
        row = by_unit[unit]
        assert row.get("predecessor_match") == predecessor_title_substring, unit


OUT_DIR = ROOT / "agreements" / "state" / "cba"

# oregon-collective-bargaining#104's "done when": these 3 current documents (the
# renamed units whose predecessor's older title only matches via `predecessor_match`)
# must each carry `supersedes`. Pinned as a data invariant, not just as a behaviour
# of matches_row()/history_picks() in isolation, so a later roster edit that drops a
# `predecessor_match` -- or a document rewrite that drops `supersedes` -- fails CI
# immediately instead of only showing up the next time someone reruns ingest.
ISSUE_104_CURRENT_IDS = (
    "state-afscme-oregon-emergency-management-2025-2027",
    "state-afscme-oregon-long-term-care-ombudsman-2025-2027",
    "state-iaff-portland-air-national-guard-firefighters-2025-2027",
)


def _frontmatter(doc_id: str) -> dict:
    path = OUT_DIR / f"{doc_id}.md"
    head = path.read_text(encoding="utf-8").split("---\n", 2)[1]
    return yaml.safe_load(head)


def test_issue_104_renamed_units_each_carry_supersedes():
    for doc_id in ISSUE_104_CURRENT_IDS:
        fm = _frontmatter(doc_id)
        assert fm["relationships"]["supersedes"], doc_id


def test_every_current_cba_with_a_superseded_same_unit_sibling_links_it():
    """Corpus-level invariant: every `status: current` state CBA that has a
    `status: superseded` sibling sharing its roster row (the same unit, a different
    term) must link that predecessor in `supersedes` or `related` -- a document is
    never left silently unpaired while its predecessor sits ingested next to it."""
    roster = yaml.safe_load(ROSTER_FILE.read_text(encoding="utf-8"))
    docs = {p.stem: _frontmatter(p.stem) for p in OUT_DIR.glob("*.md")}
    for section in ("state_contracts", "non_state_contracts"):
        for row in roster[section]:
            cur = [doc_id for doc_id, fm in docs.items()
                   if fm["status"] in ("current", "draft")
                   and ingest_cbas.matches_row(row, fm["title"])]
            pred = [doc_id for doc_id, fm in docs.items()
                    if fm["status"] == "superseded"
                    and ingest_cbas.matches_row(row, fm["title"])]
            if len(cur) != 1 or not pred:
                continue
            fm = docs[cur[0]]
            linked = set(fm["relationships"].get("supersedes") or []) | \
                set(fm["relationships"].get("related") or [])
            assert linked, (f"{cur[0]} has an ingested superseded predecessor "
                            f"({pred}) but links none of it in supersedes/related")
