"""oregon-collective-bargaining#95: OCR intermediates (`<id>.ocr.pdf`, written by
ocrmypdf beside the original -- see the OCR policy note in `src/ingest_counties.py`)
must never be committable. Investigating the issue found `.gitignore`'s existing
`_meta/snapshots/*.pdf` line already covers them -- a gitignore glob segment matches
`.` like any other character, so it does not stop at the extra dot in `.ocr.pdf`.
Verified 2026-09-12 with a REAL `ocrmypdf` run over a cached scan
(`washington-county-wcpoa-moa-longevity-and-education-pay-3-1-2024`): the produced
`.ocr.pdf` and its `.signed` sidecar left `git status --porcelain _meta/snapshots/`
clean, and 0 `.ocr.pdf` files are tracked.

These are regression locks, not a fix: nothing in this repo previously pinned this,
so narrowing `_meta/snapshots/*.pdf` in some future gitignore edit (e.g. to
`_meta/snapshots/[!.]*.pdf`, to stop excluding a legitimately-named source) would
silently reopen #95 with no test failing. `*.pdf` is intentionally NOT narrowed here
to exclude only `.ocr.pdf`: no raw source PDF is ever committed either
(`snapshot_policy: hash-only`), so there is no legitimately-named `.pdf` source this
pattern could wrongly swallow -- narrowing it would remove real coverage for no
benefit.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _check_ignore(rel_path: str) -> bool:
    """True if git considers `rel_path` (relative to REPO_ROOT) ignored."""
    result = subprocess.run(["git", "check-ignore", "-q", rel_path], cwd=REPO_ROOT)
    return result.returncode == 0


def test_a_representative_ocr_pdf_intermediate_is_ignored():
    assert _check_ignore(
        "_meta/snapshots/some-county-some-agreement-2025-2029.ocr.pdf"), (
        "an .ocr.pdf derived copy must be gitignored -- oregon-collective-"
        "bargaining#95")


def test_the_digital_signature_marker_sidecar_is_ignored():
    assert _check_ignore("_meta/snapshots/some-county-some-agreement.signed")


def test_a_real_ocr_pdf_written_to_disk_leaves_git_status_clean(tmp_path):
    """Not just the pattern -- the actual file, actually on disk, actually leaves
    `git status --porcelain` reporting nothing. This is what #95's first acceptance
    criterion asks to be demonstrated.

    HERMETIC (code review finding 7, first bullet, fix/safe-reingest): the original
    version of this test wrote its probe straight into the REAL `_meta/snapshots/`
    and asserted the WHOLE directory's `git status --porcelain` was empty. Any
    unrelated dirt already sitting there -- e.g. a legitimate new `.txt` from a real
    ingest, which is untracked and NOT ignored -- reds this test for a reason that
    has nothing to do with #95, misdirecting the reader here. This uses a scratch
    git repo (under `tmp_path`, like every other test in this suite) carrying only
    this repo's REAL `.gitignore` and an empty `_meta/snapshots/` -- nothing else
    can ever be dirty in it, so a red here can only mean the pattern itself stopped
    covering `.ocr.pdf`."""
    repo = tmp_path / "scratch-repo"
    (repo / "_meta" / "snapshots").mkdir(parents=True)
    shutil.copy(REPO_ROOT / ".gitignore", repo / ".gitignore")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    probe = repo / "_meta" / "snapshots" / "test-95-regression-probe.ocr.pdf"
    probe.write_bytes(b"%PDF-1.4 not a real pdf, just a probe for #95\n")

    result = subprocess.run(
        ["git", "status", "--porcelain", "_meta/snapshots/"],
        cwd=repo, capture_output=True, text=True, check=True)
    assert result.stdout == "", (
        "a real .ocr.pdf on disk must not appear in git status -- got: "
        f"{result.stdout!r}")


def test_no_ocr_pdf_is_currently_tracked():
    """#95's fifth acceptance criterion: 'as of this filing none are' tracked --
    verified, not assumed. If this ever fails, `git rm --cached` is the fix named
    in the issue, not a change to this test."""
    result = subprocess.run(["git", "ls-files", "_meta/snapshots/*.ocr.pdf"],
                            cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    assert result.stdout == ""
