#!/usr/bin/env python3
"""Is a committed snapshot extraction good enough to publish as verbatim text?

  python3 src/extraction_quality.py            # audit every snapshot
  python3 src/extraction_quality.py --check    # exit 1 if a NEW failure appears

THE GATE THE PROVENANCE CHECK CANNOT BE. `corpus-verify-provenance` compares the
document body against the snapshot and requires >= 70% coverage of it. That is
exactly the wrong shape of check for this failure: when the extraction itself is
garbage, body and snapshot are garbage together, coverage is 100%, and the gate
goes green while the corpus publishes noise as the terms of a labor contract.
Reproducing a source faithfully is worthless if the source was never read.

Measured 2026-08-03 across 232 committed extractions, 4 are not usable:

  RAW PDF          benton-county-...-local-2064-lab -- 1.34 MB whose first bytes
                   are `%PDF-1.6`. A PDF was copied to a .txt name; no extraction
                   ever ran. Would have published 1.3 MB of binary as an agreement.
  ENCODING DAMAGE  washington-county-wcpoa-ecu-agreement-2025-2028 (47,103 control
                   bytes) and washington-county-foppo-loa-movement-to-a-higher-
                   classification-pdf. The PDFs use a custom font encoding that
                   pdftotext could not map, so the output is a CIPHER of the real
                   words -- `0123456789yy897y` where the title belongs. This is the
                   dangerous class: it is text-shaped, it has a plausible byte
                   count, and only the alphabetic ratio gives it away.
  FRAGMENT         yamhill-county-2023-to-2026-ycea-cba -- 2,733 characters from a
                   53-page agreement (52 chars/page against a corpus median of
                   2,765). The 46 leading form feeds are 46 pages that yielded
                   nothing: an image-only front section with a text-layer tail.
                   Clean text, honestly extracted, and about 2% of the contract --
                   which is worse than an obvious failure, because it reads fine.

SPARSENESS IS NOT DAMAGE. Two documents sit just above the fragment floor and
were read end to end before being kept: lane-county-afscme-general-cba-
modifications (352 chars/page) and clackamas-county-2023-26-ratification-moa (398)
are short MOUs whose page counts include signature and mostly-blank pages. Their
text is complete. A floor set to exclude them would drop real agreements, so the
floor is 300 and the two are measured, not assumed.

WHY DERIVED RATHER THAN A LIST. A hardcoded exclusion list is right exactly once.
These four are what the RULES below currently catch; re-running is what keeps the
answer true after the next ingest. --check fails on any failure not named in
KNOWN_FAILURES, so a newly broken extraction stops a PR instead of being published.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "_meta" / "snapshots"
AGREEMENTS = ROOT / "agreements"

# Below this share of non-space characters being ASCII letters, the "text" is not
# prose in English. Real extractions here measure 0.70-0.95; the damaged ones 0.01-0.07.
MIN_ALPHA_RATIO = 0.45
# Control characters other than tab/newline/form-feed, as a share of all bytes.
# Form feed is legitimate -- it is how pdftotext marks a page break.
MAX_CONTROL_RATIO = 0.01
# Characters per source page, below which an extraction is a fragment rather than a
# sparse document. See SPARSENESS IS NOT DAMAGE above.
MIN_CHARS_PER_PAGE = 300

# The failures the rules above find today. --check treats anything NOT in here as
# a regression; entries here that stop failing are reported as fixed.
KNOWN_FAILURES = {
    "benton-county-american-federation-of-state-county-and-municipal-employees-council-75-afl-cio-local-2064-lab":
        "raw PDF committed under a .txt name; no extraction ever ran",
    "washington-county-wcpoa-ecu-agreement-2025-2028":
        "custom font encoding pdftotext could not map; output is a cipher, not the text",
    "washington-county-foppo-loa-movement-to-a-higher-classification-pdf":
        "custom font encoding pdftotext could not map; output is a cipher, not the text",
    "yamhill-county-2023-to-2026-ycea-cba":
        "2,733 chars from 53 pages (52/page); image-only front section yielded nothing",
}


def frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def assess(snapshot: pathlib.Path, pages: int | None = None) -> str | None:
    """Return a failure reason, or None if the extraction is usable."""
    raw = snapshot.read_bytes()
    if raw[:5] == b"%PDF-":
        return "raw PDF, not an extraction (starts with %PDF-)"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "not valid UTF-8"
    if not text.strip():
        return "empty"

    non_space = [c for c in text if not c.isspace()]
    if not non_space:
        return "whitespace only"
    alpha = sum(1 for c in non_space if c.isalpha() and ord(c) < 128) / len(non_space)
    if alpha < MIN_ALPHA_RATIO:
        return f"alphabetic ratio {alpha:.2f} < {MIN_ALPHA_RATIO} (encoding damage)"

    control = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t\f")
    if control > len(text) * MAX_CONTROL_RATIO:
        return f"{control:,} control characters ({control / len(text):.1%}) (encoding damage)"

    if pages and pages > 0:
        per_page = len(text) / pages
        if per_page < MIN_CHARS_PER_PAGE:
            return (f"{len(text):,} chars from {pages} pages ({per_page:.0f}/page "
                    f"< {MIN_CHARS_PER_PAGE}) (fragment)")
    return None


def audit() -> dict[str, str]:
    """doc_id -> failure reason, for every document with a committed extraction."""
    failures: dict[str, str] = {}
    for path in sorted(AGREEMENTS.rglob("*.md")):
        fm = frontmatter(path)
        doc_id = fm.get("id")
        if not doc_id:
            continue
        snap = SNAPSHOTS / f"{fm.get('snapshot_id') or doc_id}.txt"
        if not snap.is_file():
            continue  # metadata-only doc; content_exception covers it
        notes = fm.get("conversion_notes") or ""
        m = re.search(r"(\d+)\s+pages", notes)
        reason = assess(snap, int(m.group(1)) if m else None)
        if reason:
            failures[doc_id] = reason
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on any failure not listed in KNOWN_FAILURES")
    args = ap.parse_args()

    failures = audit()
    total = len(list(SNAPSHOTS.glob("*.txt")))
    print(f"{total} committed extraction(s); {len(failures)} unusable\n")
    for doc_id, reason in sorted(failures.items()):
        mark = "known" if doc_id in KNOWN_FAILURES else "NEW"
        print(f"  [{mark:5}] {doc_id}\n           {reason}")

    if not args.check:
        return 0

    new = set(failures) - set(KNOWN_FAILURES)
    fixed = set(KNOWN_FAILURES) - set(failures)
    if fixed:
        print(f"\n{len(fixed)} known failure(s) now pass — remove them from "
              f"KNOWN_FAILURES and promote the text:")
        for doc_id in sorted(fixed):
            print(f"    {doc_id}")
    if new:
        print(f"\n{len(new)} NEW unusable extraction(s). An extraction that cannot "
              f"be read must not be published as an agreement's terms — fix the "
              f"extraction, or give the document a content_exception:", file=sys.stderr)
        for doc_id in sorted(new):
            print(f"    {doc_id}: {failures[doc_id]}", file=sys.stderr)
        return 1
    print("\nNo new extraction failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
