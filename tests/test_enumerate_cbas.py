"""`src/enumerate_cbas.py` writes `_meta/sources/state.yml`, the manifest for the state
tier -- 512 of this corpus's 677 sources. `corpus-detect-changes --record-baseline`
writes a real `sha256` onto each source once it has been fetched; `enumerate_cbas.py`
re-derives the whole `sources:` list from a fresh SharePoint listing every time it
runs, because ids/urls/titles/families are its data, not the drift checker's.

`sha256` is NOT enumerate_cbas.py's field -- it is corpus-detect-changes's, carried
here only so the manifest stays one file. A re-enumeration must not step on it: for a
source whose `url` is unchanged, the recorded baseline is that source's own history
and must survive the rewrite untouched (oregon-collective-bargaining#14's Agent Brief
keys this on `url`, not `id` -- see `src/_manifest_baseline.py`). Losing it here is
silent -- nothing red-flags a group file that "generated successfully" with
`sha256: ""` on 512 previously-seeded sources, and the next drift run would report
all 512 as newly unseeded.

`src/discover_counties.py` carries this same rule for the 12 county manifests via the
same shared `_manifest_baseline.carry_recorded_sha256` this module's `_carry_recorded`
delegates to.

Two of these tests (`test_main_*`) drive `main()` itself rather than calling
`_carry_recorded`/`render` directly. That is deliberate: the #14 code review found
that a suite exercising only the helpers passed green through 3 of 4 ways the
baseline-wipe bug returns, including deleting the one `main()` line that calls
`_carry_recorded` at all -- "the regression lock does not lock the regression."
Driving the real pipeline is what makes that mutation, and a reverted `render()`,
both fail here.
"""
from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import enumerate_cbas  # noqa: E402


REAL_STATE_YML = REPO_ROOT / "_meta" / "sources" / "state.yml"


def _real_committed_source() -> dict:
    """A source id/url + its currently-recorded baseline, read from the real
    committed manifest -- not a hand-authored fixture. Using the manifest actually
    in the repo is the point: this baseline is what a careless re-enumeration would
    destroy. The FIRST source that already carries a baseline, not index 0: index 0
    is whatever `build_sources()`'s filename sort currently puts first, which is
    real corpus content and will legitimately change (a DAS posting that sorts
    before today's first file) -- coupling the fixture precondition to a specific
    row makes the suite red on a correct manifest. Every one of the 512 state
    sources already carries a baseline as of #14, so this is not a narrower search
    than `index=0` was; it is just not fragile to which row happens to be first."""
    data = yaml.safe_load(REAL_STATE_YML.read_text(encoding="utf-8"))
    return next(s for s in data["sources"] if s.get("sha256"))


def test_carry_recorded_preserves_baseline_for_a_still_present_url():
    """A source enumeration re-derives with the SAME url keeps its recorded sha256,
    exactly as the county-tier `_carry_recorded` does. `last_checked` is NOT carried
    -- it is enumeration's own field (`_strip_dates` documents that it "moves on
    every run by design"); this run's own last_checked must win, not the baseline's
    original seed date."""
    committed = _real_committed_source()

    fresh = [{
        "id": committed["id"],
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",  # what build_sources() always emits -- unseeded until carried
        "title": committed["title"],
        "last_checked": "2026-08-27",  # today's enumeration run
    }]

    enumerate_cbas._carry_recorded(fresh)

    assert fresh[0]["sha256"] == committed["sha256"]
    assert fresh[0]["last_checked"] == "2026-08-27", (
        "last_checked must reflect THIS run, not be frozen at the baseline's "
        "original seed date")


def test_carry_recorded_leaves_a_brand_new_id_unseeded():
    """A source discovery has never seen before must stay `sha256: ""` -- that is
    drift detection's field to fill via --record-baseline, not this generator's to
    invent or leave stale."""
    fresh = [{
        "id": "state-a-cba-nobody-has-ever-recorded",
        "url": "https://www.oregon.gov/das/HR/CBA/brand-new.pdf",
        "family": "cba",
        "format": "pdf",
        "sha256": "",
        "title": "Brand New CBA",
        "last_checked": "2026-08-27",
    }]

    enumerate_cbas._carry_recorded(fresh)

    assert fresh[0]["sha256"] == ""


def test_carry_recorded_follows_url_not_id():
    """The join key is `url`, per #14's Agent Brief ("source_url is the reliable
    key") and its explicit join hazard: a file relocated within the library keeps
    its slug/id but is served from a different url. A rename that keeps the SAME
    url must still carry (the id changed, nothing about the underlying fetch did);
    a source whose id happens to match but whose url moved must NOT carry (it is
    now a different fetch and has no history yet)."""
    committed = _real_committed_source()

    # Same url, different id (e.g. the SharePoint filename/title changed but the
    # library path did not) -- must still carry.
    renamed = [{
        "id": "state-this-id-is-not-the-committed-one",
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",
        "title": "A retitled version of the same file",
        "last_checked": "2026-08-27",
    }]
    enumerate_cbas._carry_recorded(renamed)
    assert renamed[0]["sha256"] == committed["sha256"], (
        "an id change at an unchanged url must still carry the baseline")

    # Same id, different url (e.g. the same slug now resolves to a relocated file)
    # -- must NOT carry; this is a different fetch with no recorded history.
    relocated = [{
        "id": committed["id"],
        "url": "https://www.oregon.gov/das/HR/CBA/some-other-file-entirely.pdf",
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",
        "title": committed["title"],
        "last_checked": "2026-08-27",
    }]
    enumerate_cbas._carry_recorded(relocated)
    assert relocated[0]["sha256"] == "", (
        "an id match at a CHANGED url must not inherit the old url's baseline")


def test_render_quotes_sha256_matching_record_baselines_own_style():
    """`corpus-detect-changes --record-baseline` writes `sha256: "<hex>"` (quoted).
    `yaml.safe_dump` on a plain str writes `sha256: <hex>` (bare). Two writers touching
    one field in different styles turns every real diff into quote-style noise -- the
    exact failure `src/discover_counties.py`'s `_Quoted`/`_Dumper` pair exists to
    prevent (see `src/_manifest_baseline.py`). enumerate_cbas.render() must use the
    same convention.
    """
    committed = _real_committed_source()
    sources = [{
        "id": committed["id"],
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": enumerate_cbas._Quoted(committed["sha256"]),
        "title": committed["title"],
        "last_checked": committed["last_checked"],
    }]

    text = enumerate_cbas.render(sources, report=[], today="2026-08-27")

    assert f'sha256: "{committed["sha256"]}"' in text


def test_main_preserves_baseline_through_the_real_pipeline(tmp_path, monkeypatch):
    """Drives `main()` itself, not `_carry_recorded()` in isolation.

    This is the regression lock the #14 review found missing: with only
    `_carry_recorded` under direct test, deleting the single `_carry_recorded(sources)`
    call inside `main()` -- the line that wires this whole fix into the pipeline --
    left every existing test green. Faking the network boundary (`fetch_files`) and
    the roster gate (`reconcile`, whose own correctness is someone else's test) while
    running the REAL `main()` against a scratch copy of the committed manifest closes
    that gap: this test fails if that wiring is ever removed again.
    """
    committed = _real_committed_source()
    # Reconstruct the SharePoint file record that re-derives this exact source: `url`
    # is "https://www.oregon.gov" + quote(ServerRelativeUrl), and `title` is the
    # filename with its extension stripped, so title + ".pdf" round-trips through
    # slug() back to the committed id.
    # build_sources() quotes ServerRelativeUrl itself, so the RAW (unquoted) path is
    # what a fetch_files() record carries -- feeding back the already-quoted form
    # would double-encode it and the reconstructed url would not match committed["url"].
    server_relative_url = urllib.parse.unquote(
        committed["url"].removeprefix("https://www.oregon.gov"))
    name = server_relative_url.rsplit("/", 1)[-1]
    assert enumerate_cbas.slug(name) == committed["id"], (
        "test setup bug: reconstructed filename does not round-trip to the "
        "committed id -- fix the reconstruction, not the assertion below")

    scratch = tmp_path / "state.yml"
    scratch.write_text(REAL_STATE_YML.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(enumerate_cbas, "GROUP_FILE", scratch)
    # main()'s success print does GROUP_FILE.relative_to(REPO_ROOT); move REPO_ROOT
    # along with it so that print does not raise on an unrelated tmp path.
    monkeypatch.setattr(enumerate_cbas, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(enumerate_cbas, "fetch_files",
                        lambda: [{"Name": name, "ServerRelativeUrl": server_relative_url,
                                   "TimeLastModified": "2026-08-27T00:00:00Z", "Length": "1"}])
    # Roster reconciliation is out of scope for this test (it is exercised by
    # reconcile()'s own callers/fixtures elsewhere in this file's docstring
    # coverage); a real roster fed only one synthetic file would ABORT on every
    # unmatched row and never reach render() at all.
    monkeypatch.setattr(enumerate_cbas, "reconcile", lambda files, roster: ([], []))
    monkeypatch.setattr(sys, "argv", ["enumerate_cbas.py"])

    rc = enumerate_cbas.main()

    assert rc == 0
    written = yaml.safe_load(scratch.read_text(encoding="utf-8"))
    out_source = next(s for s in written["sources"] if s["id"] == committed["id"])
    assert out_source["sha256"] == committed["sha256"], (
        "main() did not preserve the recorded baseline -- the _carry_recorded() "
        "call site inside main() is not wired in")
    assert f'sha256: "{committed["sha256"]}"' in scratch.read_text(encoding="utf-8"), (
        "main() wrote the baseline unquoted -- render() regressed to yaml.safe_dump's "
        "bare-string style")
