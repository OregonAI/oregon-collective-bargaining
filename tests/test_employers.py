"""`_meta/employers.yml` absence-discipline gate.

Issue #8 (operator decision, 2026-09-12): records requests for the counties with no
located CBA are DECLINED, not deferred -- the agent work that replaces them is to make
the registry itself honest about *why* each unbuilt county is unbuilt. Before this
test, 25 unbuilt rows carried only `survey_status`, a single-word category, with no
reason text and no date a reader could check against a later re-test. A reader (or an
agent citing this corpus) could not tell "the county blocks us" from "nobody has
looked yet" without reading this GitHub issue -- and nothing stopped a sentence like
"County X has no agreements" from being written, which AGENTS.md's absence-discipline
line (#4) forbids: "could not check" must never collapse into "is not there".

This test is data-only, like `test_discover_counties.py`'s regression lock: it reads
the real committed file (`_meta/employers.yml`), not a fixture, because the fact under
test IS what is committed -- a fixture would test the validator, not the registry.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EMPLOYERS = REPO_ROOT / "_meta" / "employers.yml"

# Phrasing that would assert the county has no agreements, rather than reporting
# our own search/access limit (AGENTS.md absence-discipline, #4).
_ABSENCE_ASSERTIONS = re.compile(
    r"\bhas no (collective bargaining |labor )?agreements?\b"
    r"|\bdoes not have (any )?agreements?\b"
    r"|\bno agreements? exists?\b",
    re.I,
)


def _load() -> dict:
    return yaml.safe_load(EMPLOYERS.read_text(encoding="utf-8"))


def _raw() -> str:
    return EMPLOYERS.read_text(encoding="utf-8")


def _unbuilt(employers: list[dict]) -> list[dict]:
    return [e for e in employers if not e["built"]]


def test_every_unbuilt_employer_carries_a_reason_and_a_date():
    """Every `built: false` row must state WHY and WHEN that was established --
    the issue's core ask. Without this, "not built" is indistinguishable from
    "nobody recorded anything"."""
    employers = _load()["employers"]
    unbuilt = _unbuilt(employers)
    assert unbuilt, "expected at least one unbuilt employer to check"
    missing_reason = [e["slug"] for e in unbuilt if not e.get("status_reason")]
    missing_date = [e["slug"] for e in unbuilt if not e.get("status_reason_date")]
    assert not missing_reason, f"unbuilt employers with no status_reason: {missing_reason}"
    assert not missing_date, f"unbuilt employers with no status_reason_date: {missing_date}"


def test_status_reason_dates_are_real_iso_dates_not_in_the_future():
    employers = _load()["employers"]
    today = datetime.date.today()
    for e in _unbuilt(employers):
        raw = e["status_reason_date"]
        d = datetime.date.fromisoformat(str(raw))
        assert d <= today, f"{e['slug']}: status_reason_date {raw} is in the future"


def test_no_unbuilt_employer_is_worded_as_having_no_agreements():
    """The middle category (not-located / not-investigated) is a statement about
    OUR search, never about the county's labor relations. Oregon counties bargain;
    ORS 243 requires it."""
    employers = _load()["employers"]
    for e in _unbuilt(employers):
        assert not _ABSENCE_ASSERTIONS.search(e["status_reason"]), (
            f"{e['slug']}: status_reason reads as an absence claim: {e['status_reason']!r}"
        )


def test_could_not_verify_counties_record_that_the_agreements_are_published():
    """Linn and Douglas: the county publishes the agreements; OUR fetch is blocked.
    That is the opposite claim from 'not-located' and must read differently."""
    employers = {e["slug"]: e for e in _load()["employers"]}
    for slug in ("linn-county", "douglas-county"):
        e = employers[slug]
        assert e["survey_status"] == "could-not-verify"
        reason = e["status_reason"].lower()
        assert "publish" in reason, f"{slug}: status_reason should say the county publishes these"
        assert "403" in reason, f"{slug}: status_reason should record the measured HTTP status"


def test_could_not_verify_counties_were_retested_after_the_operator_ruling():
    """Acceptance criterion: re-test before writing the 403 claim, with the
    corpus-toolkit Fetcher (curl and the toolkit disagree on some hosts)."""
    employers = {e["slug"]: e for e in _load()["employers"]}
    for slug in ("linn-county", "douglas-county"):
        e = employers[slug]
        reason = e["status_reason"].lower()
        assert "fetcher" in reason, f"{slug}: status_reason should name the corpus-toolkit Fetcher"
        # The re-test date must be no older than the operator's 2026-09-12 ruling
        # that reopened this as a re-test-before-writing requirement.
        retest_date = datetime.date.fromisoformat(str(e["status_reason_date"]))
        assert retest_date >= datetime.date(2026, 9, 12), (
            f"{slug}: status_reason_date predates the operator's re-test requirement"
        )


def test_not_located_counties_record_the_search_date_not_an_absence_claim():
    employers = {e["slug"]: e for e in _load()["employers"]}
    for slug in ("polk-county", "josephine-county", "umatilla-county", "klamath-county"):
        e = employers[slug]
        assert e["survey_status"] == "not-located"
        reason = e["status_reason"].lower()
        assert "locat" in reason


def test_jackson_records_the_outstanding_afscme_unit_and_the_michigan_lead():
    """Jackson stays `built: true` / `verified` (issue: do not change that) but is
    only partially held -- the one gap and the dead lead both need recording so
    nobody re-chases mijackson.org."""
    employers = {e["slug"]: e for e in _load()["employers"]}
    jackson = employers["jackson-county"]
    assert jackson["built"] is True
    assert jackson["survey_status"] == "verified"
    reason = jackson.get("status_reason", "")
    assert "afscme" in reason.lower()
    assert "michigan" in reason.lower()
    assert "erb" in reason.lower(), (
        "jackson-county: status_reason should flag the JCSSA document as an ERB "
        "case exhibit, not the employer's own posted copy"
    )


def test_benton_built_true_is_not_left_recorded_as_not_located():
    """Found while surveying this file: Benton carries `built: true` (3 agreements
    committed under agreements/benton-county/) but `survey_status: not-located` and
    a null `source_url` -- leftover from the original 2026-08-02 survey, before the
    tranche-2 hunt in `src/discover_counties.py` found the real index one navigation
    level below where the survey looked. A reader trusting `survey_status` alone
    would conclude Benton has no located index, which is simply false."""
    employers = {e["slug"]: e for e in _load()["employers"]}
    benton = employers["benton-county"]
    assert benton["built"] is True
    assert benton["survey_status"] == "verified"
    assert benton["source_url"]


def test_built_true_employers_have_verified_survey_status():
    """General form of the Benton bug: a committed, built employer cannot be
    honestly labelled anything other than `verified` -- we verified it by building
    it. Catches the next stale row before it needs its own named test."""
    employers = _load()["employers"]
    mismatched = [e["slug"] for e in employers
                  if e["built"] and e["survey_status"] != "verified"]
    assert not mismatched, f"built employers not marked verified: {mismatched}"


def test_registry_records_the_operator_decision_not_to_file_records_requests():
    """Acceptance criterion: the declined records-request option must read as
    DECLINED, not merely absent/pending, and must carry its date -- in the
    registry's own header, the precedent `oregon-counties/_meta/counties.yml` uses
    for the analogous Verified-Bots closure.

    Scoped to the header comment block (everything before the first `employers:`
    line) so this cannot be satisfied by the per-row status_reason text instead --
    deleting the header's CLOSED note must fail this test."""
    raw = _raw()
    header = raw.split("\nemployers:", 1)[0]
    assert "CLOSED, 2026-09-12" in header
    assert re.search(r"declin", header, re.I)
    assert "#8" in header
