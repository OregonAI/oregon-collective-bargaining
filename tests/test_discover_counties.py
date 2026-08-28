"""`src/discover_counties.py` writes the 12 county source manifests. Its
`_carry_recorded` already fixed the "regeneration wipes the drift baseline" bug for
the county tier (see its docstring). This is a regression lock for that fix: nothing
in this repo currently pins it, so a future edit to `_carry_recorded` or `render()`
could silently reintroduce the wipe with no test failing.

Same seam decision as `tests/test_enumerate_cbas.py`, same reason: read a real id +
its currently-recorded baseline out of a committed group file (`benton.yml`, the
smallest -- 3 sources), rather than a hand-authored fixture.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import discover_counties  # noqa: E402


REAL_BENTON_YML = REPO_ROOT / "_meta" / "sources" / "benton.yml"


def _real_committed_source(index: int = 0) -> dict:
    data = yaml.safe_load(REAL_BENTON_YML.read_text(encoding="utf-8"))
    return data["sources"][index]


def test_carry_recorded_preserves_baseline_for_a_still_present_id():
    committed = _real_committed_source(0)
    assert committed["sha256"], "fixture precondition: benton.yml must already carry a baseline"

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
    assert fresh[0]["last_checked"] == committed["last_checked"]


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
