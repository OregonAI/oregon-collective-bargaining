"""`src/enumerate_cbas.py` writes `_meta/sources/state.yml`, the manifest for the state
tier -- 512 of this corpus's 677 sources. `corpus-detect-changes --record-baseline`
writes a real `sha256` onto each source once it has been fetched; `enumerate_cbas.py`
re-derives the whole `sources:` list from a fresh SharePoint listing every time it
runs, because ids/urls/titles/families are its data, not the drift checker's.

`sha256` is NOT enumerate_cbas.py's field -- it is corpus-detect-changes's, carried
here only so the manifest stays one file. A re-enumeration must not step on it: for a
source whose id is unchanged, the recorded baseline is that source's own history and
must survive the rewrite untouched. Losing it here is silent -- nothing red-flags a
group file that "generated successfully" with `sha256: ""` on 512 previously-seeded
sources, and the next drift run would report all 512 as newly unseeded.

`src/discover_counties.py` already carries this rule for the 12 county manifests
(`_carry_recorded`, corpus-toolkit's sibling fix for the county tier -- see its
docstring). This test pins the same contract for the state tier, which does not yet
have it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import enumerate_cbas  # noqa: E402


REAL_STATE_YML = REPO_ROOT / "_meta" / "sources" / "state.yml"


def _real_committed_source(index: int = 0) -> dict:
    """A source id + its currently-recorded baseline, read from the real committed
    manifest -- not a hand-authored fixture. Using the manifest actually in the repo
    is the point: this baseline is what a careless re-enumeration would destroy."""
    data = yaml.safe_load(REAL_STATE_YML.read_text(encoding="utf-8"))
    return data["sources"][index]


def test_carry_recorded_preserves_baseline_for_a_still_present_id():
    """A source enumeration re-derives with the SAME id keeps its recorded sha256
    and last_checked, exactly as the county-tier `_carry_recorded` does."""
    committed = _real_committed_source(0)
    assert committed["sha256"], "fixture precondition: the real manifest must already carry a baseline"

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
    assert fresh[0]["last_checked"] == committed["last_checked"]


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


def test_render_quotes_sha256_matching_record_baselines_own_style():
    """`corpus-detect-changes --record-baseline` writes `sha256: "<hex>"` (quoted).
    `yaml.safe_dump` on a plain str writes `sha256: <hex>` (bare). Two writers touching
    one field in different styles turns every real diff into quote-style noise -- the
    exact failure `src/discover_counties.py`'s `_Quoted`/`_Dumper` pair exists to
    prevent (see its docstring). enumerate_cbas.render() must use the same convention.
    """
    committed = _real_committed_source(0)
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
