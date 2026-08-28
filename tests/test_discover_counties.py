"""`src/discover_counties.py` writes the 12 county source manifests. Its
`_carry_recorded` already fixed the "regeneration wipes the drift baseline" bug for
the county tier (see its docstring) by delegating to the shared
`_manifest_baseline.carry_recorded_sha256`. This is a regression lock for that fix:
nothing in this repo currently pins it, so a future edit to `_carry_recorded` or
`render()` could silently reintroduce the wipe with no test failing.

Same seam decision as `tests/test_enumerate_cbas.py`, same reason: read a real id/url
+ its currently-recorded baseline out of a committed group file (`benton.yml`, the
smallest -- 3 sources), rather than a hand-authored fixture.

`test_main_*` drives `main()` itself against the REAL archived Benton fetch under
`_meta/discovery/`, not `_carry_recorded()`/`render()` in isolation. The #14 code
review measured that a suite exercising only the helpers passed green through 3 of 4
ways the baseline-wipe bug returns -- including reverting `render()` to
`yaml.safe_dump`, which nothing here previously caught (the state tier had a
render-quoting test; the county tier did not). Both gaps are closed below.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import discover_counties  # noqa: E402


REAL_BENTON_YML = REPO_ROOT / "_meta" / "sources" / "benton.yml"


def _real_committed_source() -> dict:
    """The FIRST source that already carries a baseline, not index 0 -- same
    fragility this file's sibling (`tests/test_enumerate_cbas.py`) avoids: index 0
    is whatever the extractor's page order currently puts first, real corpus
    content that can legitimately change. All 3 of benton.yml's sources already
    carry a baseline as of #14, so this is not a narrower search than index 0 was."""
    data = yaml.safe_load(REAL_BENTON_YML.read_text(encoding="utf-8"))
    return next(s for s in data["sources"] if s.get("sha256"))


def test_carry_recorded_preserves_baseline_for_a_still_present_url():
    """`last_checked` is NOT carried -- it is discovery's own field, set from
    `ARCHIVE_DATE` at build time; this run's own value must win, not a prior
    baseline's seed-time value (same reasoning as the state-tier test)."""
    committed = _real_committed_source()

    fresh = [{
        "id": committed["id"],
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",  # what the extractors always emit -- unseeded until carried
        "title": committed["title"],
        "last_checked": "2026-08-27",
    }]

    discover_counties._carry_recorded("benton", fresh)

    assert fresh[0]["sha256"] == committed["sha256"]
    assert fresh[0]["last_checked"] == "2026-08-27", (
        "last_checked must reflect THIS run, not be frozen at the baseline's "
        "original seed date")


def test_carry_recorded_leaves_a_brand_new_id_unseeded():
    fresh = [{
        "id": "benton-a-cba-nobody-has-ever-recorded",
        "url": "https://www.co.benton.or.us/some/brand-new.pdf",
        "family": "cba",
        "format": "pdf",
        "sha256": "",
        "title": "Brand New CBA",
        "last_checked": "2026-08-27",
    }]

    discover_counties._carry_recorded("benton", fresh)

    assert fresh[0]["sha256"] == ""


def test_carry_recorded_is_a_no_op_for_a_county_with_no_committed_file():
    """A county discovery has never run for (no committed group file yet) must not
    crash -- there is nothing to carry forward, so every source stays as build_sources
    left it."""
    fresh = [{
        "id": "nowhere-county-some-cba",
        "url": "https://example.invalid/x.pdf",
        "family": "cba",
        "format": "pdf",
        "sha256": "",
        "title": "X",
        "last_checked": "2026-08-27",
    }]

    discover_counties._carry_recorded("nowhere-county-does-not-exist", fresh)

    assert fresh[0]["sha256"] == ""


def test_carry_recorded_follows_url_not_id():
    """The join key is `url`, per #14's Agent Brief -- a rename at an unchanged url
    must still carry; an id match at a CHANGED url must not inherit a baseline that
    belongs to a different fetch."""
    committed = _real_committed_source()

    renamed = [{
        "id": "benton-this-id-is-not-the-committed-one",
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",
        "title": "A retitled version of the same file",
        "last_checked": "2026-08-27",
    }]
    discover_counties._carry_recorded("benton", renamed)
    assert renamed[0]["sha256"] == committed["sha256"], (
        "an id change at an unchanged url must still carry the baseline")

    relocated = [{
        "id": committed["id"],
        "url": "https://hr.bentoncountyor.gov/some-other-file-entirely.pdf",
        "family": committed["family"],
        "format": committed["format"],
        "sha256": "",
        "title": committed["title"],
        "last_checked": "2026-08-27",
    }]
    discover_counties._carry_recorded("benton", relocated)
    assert relocated[0]["sha256"] == "", (
        "an id match at a CHANGED url must not inherit the old url's baseline")


def test_render_quotes_sha256_matching_record_baselines_own_style():
    """`corpus-detect-changes --record-baseline` writes `sha256: "<hex>"` (quoted).
    `yaml.safe_dump` on a plain str writes `sha256: <hex>` (bare). The state tier
    (`tests/test_enumerate_cbas.py`) already pinned this for its `render()`; this
    repo's county-tier `render()` had no equivalent lock, which is exactly the gap
    the #14 review found: reverting `discover_counties.render()` to `yaml.safe_dump`
    passed every existing test.
    """
    committed = _real_committed_source()
    cfg = discover_counties.COUNTIES["benton"]
    sources = [{
        "id": committed["id"],
        "url": committed["url"],
        "family": committed["family"],
        "format": committed["format"],
        "sha256": discover_counties._Quoted(committed["sha256"]),
        "title": committed["title"],
        "last_checked": committed["last_checked"],
    }]

    text = discover_counties.render("benton", cfg, sources)

    assert f'sha256: "{committed["sha256"]}"' in text


def test_main_preserves_baseline_through_the_real_pipeline(tmp_path, monkeypatch):
    """Drives `main()` itself against the REAL archived Benton fetch, not
    `_carry_recorded()`/`render()` in isolation -- the regression lock the #14
    review found missing. This fails if the `_carry_recorded(county, sources)` call
    site inside `main()` is ever removed, or if `render()` regresses to
    `yaml.safe_dump`.
    """
    committed = _real_committed_source()

    scratch_dir = tmp_path / "sources"
    scratch_dir.mkdir()
    shutil.copy(REAL_BENTON_YML, scratch_dir / "benton.yml")
    monkeypatch.setattr(discover_counties, "SOURCES_DIR", scratch_dir)
    # main()'s success print does out.relative_to(REPO_ROOT); move REPO_ROOT along
    # with SOURCES_DIR so that print does not raise on an unrelated tmp path.
    monkeypatch.setattr(discover_counties, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv",
                        ["discover_counties.py", "--only", "benton"])

    rc = discover_counties.main()

    assert rc == 0
    written = yaml.safe_load((scratch_dir / "benton.yml").read_text(encoding="utf-8"))
    out_source = next(s for s in written["sources"] if s["id"] == committed["id"])
    assert out_source["sha256"] == committed["sha256"], (
        "main() did not preserve the recorded baseline -- the _carry_recorded() "
        "call site inside main() is not wired in")
    assert f'sha256: "{committed["sha256"]}"' in (scratch_dir / "benton.yml").read_text(
        encoding="utf-8"), (
        "main() wrote the baseline unquoted -- render() regressed to yaml.safe_dump's "
        "bare-string style")
