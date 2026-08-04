#!/usr/bin/env python3
"""Promote the committed extractions into `## Full text` and flip the documents to verbatim.

  python3 src/promote_full_text.py            # rewrite bodies, frontmatter, hashes
  python3 src/promote_full_text.py --check    # exit 1 if any document is stale (CI)
  python3 src/promote_full_text.py --report   # what would change, write nothing

WHY THIS EXISTS. The corpus shipped summary-first: 237 documents whose bodies were
metadata ABOUT an agreement -- parties, term, page count -- and never its terms. The
median per-document prose was 69 words standing in for a 231-page contract, which
cannot answer the question the corpus exists to answer ("what is the grievance
procedure"). The operator's determination on 2026-08-03 flipped the class to
verbatim; this script is that flip.

THE BASIS, recorded because the recorded basis is what a skeptical reader attacks.
It is NOT "contracts are not copyrightable" -- contracts can carry copyright, and a
CBA is jointly authored with a union, which is a private party. That objection is
what made the corpus summary-first in the first place. The narrower and sturdier
ground, and the one written into corpus.yml and every document's
`reproduction_basis`, is threefold: these are public records of a public body under
ORS 192.311-192.478; the public employer ALREADY publishes the full executed PDF at
the source_url each document cites; and a ratified agreement is an official act of
that body, which Georgia v. Public.Resource.Org, 590 U.S. 255 (2020) places outside
copyright. Mirroring a document the government itself publishes in full is a much
smaller claim than the one we are declining to make.

ORDER OF OPERATIONS IS LOAD-BEARING. src/anchor_sections.py runs FIRST and rewrites
the snapshots; this script copies those anchored snapshots into the bodies and only
THEN recomputes source_sha256. That order is what keeps three separate checks true
at once:

  * provenance's in-order check -- every non-empty line of `## Full text` must appear
    in the snapshot, in order. Satisfied because the body IS the snapshot.
  * provenance's coverage floor (0.70 fail / 0.90 warn, from corpus.yml) -- satisfied
    at 1.00 for the same reason.
  * the recorded hash -- for a `snapshot_policy: hash-only` document with a committed
    .txt, the toolkit hashes the NORMALIZED TEXT of that .txt, not the source PDF's
    bytes. Anchoring changes it. Writing the body and the hash in one pass is what
    stops them drifting apart; nothing else in CI would notice if they did.

WHAT IS HELD BACK, and why holding back is the honest answer rather than a gap:

  * 4 documents whose extraction is unusable -- a raw PDF committed under a .txt
    name, two whose custom font encoding pdftotext could not map (the output is a
    cipher of the real words), and one that yielded 2% of a 53-page agreement.
    src/extraction_quality.py derives that list and owns the reasoning. Publishing
    any of them as an agreement's terms would be worse than publishing nothing,
    because it would be text-shaped.
  * 5 documents that already carry `content_exception`: image-only scans whose three
    OCR engines disagreed, so no machine reading earned the snapshot.

Those 9 keep `content_mode: summary` and gain a `content_exception` recording which
class they fall in -- which is also what keeps the corpus legible to the toolkit,
since a doc_type declared verbatim in corpus.yml fails provenance without one.

THE OCR TRANCHE IS PROMOTED, and that is a deliberate reading of the two-engine rule
rather than a bypass of it. 57 documents came from scans with no text layer, and
their `conversion_notes` record the corroboration that was already performed at
ingest: tesseract (ocrmypdf) against paddleocr PP-OCRv6, agreeing on 99% of the word
sequence and 86% of figures, against the platform's 0.80 bar. The rule asks for two
independent engines to agree before text is promotable; that happened, it is
recorded per document, and the 5 that FAILED it are the content_exception set above.
Every such document keeps its "NOT human-verified -- treat every number as unchecked"
note in the body, because corroboration is evidence the words are on the page, not
evidence a human read them.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extraction_quality  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "_meta" / "snapshots"
AGREEMENTS = ROOT / "agreements"

BASIS = ("public record of a public body (ORS 192.311-192.478); the employer publishes "
         "the executed agreement in full at source_url; a ratified agreement is an "
         "official act (Georgia v. Public.Resource.Org, 590 U.S. 255 (2020)) — "
         "mirrored in full per the class determination in corpus.yml schema.doc_types "
         "(verbatim: true)")

EXCEPTION_UNUSABLE = ("extraction is not usable text ({reason}); no verbatim text can be "
                      "published from it, so this document stays metadata-only until the "
                      "source is re-extracted")

# The summary-first paragraph the ingest wrote into every body. It is a claim that is
# no longer true, so it is removed rather than left to contradict the text below it.
SUMMARY_CLAIM = re.compile(
    r"\nThis corpus is \*\*summary-first for agreements\*\*:.*?official\s+source link above\.\n",
    re.S)

CURATOR_CLAIM = re.compile(
    r"Summary-first is the recorded class determination.*?already carries what would be diffed\.\n",
    re.S)

BANNER_SUMMARY = "This is a curated\n> summary, not the agreement's official text."
BANNER_VERBATIM = ("This is a non-authoritative\n> mirror of the agreement's text, not the "
                   "official record.")


# IMPORTED, NOT REIMPLEMENTED. The recorded hash is sha256 of the normalized snapshot
# text, and the verifier computes it with the toolkit's own normalize_ws — which does
# not only collapse whitespace, it also folds curly quotes and apostrophes to straight
# ones. A local four-line lookalike that skipped that fold was written here first and
# would have produced a mismatched hash on every agreement containing a smart quote,
# which is most of them. There is exactly one correct definition and it lives upstream.
from corpus_toolkit.repo import normalize_ws  # noqa: E402


def split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError("no frontmatter")
    return m.group(1), m.group(2)


def field(fm: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.M)
    return m.group(1).strip().strip("'\"") if m else None


def set_field(fm: str, key: str, value: str) -> str:
    """Targeted line edit, never a YAML re-dump — hand formatting must survive."""
    quoted = "'" + value.replace("'", "''") + "'"
    pattern = rf"^{re.escape(key)}:.*?(?=\n[a-zA-Z_]+:|\n---|\Z)"
    if re.search(pattern, fm, re.S | re.M):
        return re.sub(pattern, f"{key}: {quoted}", fm, count=1, flags=re.S | re.M)
    # Insert before the closing delimiter if the key is absent.
    return fm[:-4] + f"{key}: {quoted}\n" + fm[-4:]


def build_body(body: str, snapshot_text: str) -> str:
    """Replace the summary-first claims and append `## Full text`."""
    out = SUMMARY_CLAIM.sub("\n", body)
    out = CURATOR_CLAIM.sub(
        "The full executed text is mirrored below from the committed extraction; the\n"
        "official PDF at the source link above remains the authoritative record.\n", out)
    out = out.replace(BANNER_SUMMARY, BANNER_VERBATIM)
    out = re.sub(r"\n## Full text\n.*$", "\n", out, flags=re.S)
    return out.rstrip("\n") + "\n\n## Full text\n\n" + snapshot_text.rstrip("\n") + "\n"


def plan() -> tuple[list, list]:
    """(promotable, held_back) as lists of (path, doc_id, snapshot_path_or_reason)."""
    unusable = extraction_quality.audit()
    promote, hold = [], []
    for path in sorted(AGREEMENTS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(text)
        doc_id = field(fm, "id")
        snap = SNAPSHOTS / f"{field(fm, 'snapshot_id') or doc_id}.txt"
        if field(fm, "content_exception"):
            hold.append((path, doc_id, "pre-existing content_exception"))
        elif doc_id in unusable:
            hold.append((path, doc_id, unusable[doc_id]))
        elif not snap.is_file():
            hold.append((path, doc_id, "no committed extraction"))
        else:
            promote.append((path, doc_id, snap))
    return promote, hold


def render(path: pathlib.Path, snap: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    snapshot_text = snap.read_text(encoding="utf-8", errors="replace")
    digest = hashlib.sha256(normalize_ws(snapshot_text).encode("utf-8")).hexdigest()
    fm = set_field(fm, "content_mode", "verbatim")
    fm = set_field(fm, "reproduction_basis", BASIS)
    fm = re.sub(r"^source_sha256:.*$", f"source_sha256: {digest}", fm, count=1, flags=re.M)
    return fm + build_body(body, snapshot_text)


def render_held(path: pathlib.Path, reason: str) -> str:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if field(fm, "content_exception"):
        return text  # already excused and correctly so; leave it alone
    fm = set_field(fm, "content_exception", EXCEPTION_UNUSABLE.format(reason=reason))
    return fm + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    promote, hold = plan()
    if args.report:
        print(f"promote: {len(promote)}   hold back: {len(hold)}\n")
        for _, doc_id, reason in hold:
            print(f"  HOLD  {doc_id}\n        {reason}")
        return 0

    stale, written = [], 0
    for path, doc_id, snap in promote:
        new = render(path, snap)
        if new != path.read_text(encoding="utf-8"):
            stale.append(doc_id)
            if not args.check:
                path.write_text(new, encoding="utf-8")
                written += 1
    for path, doc_id, reason in hold:
        new = render_held(path, reason)
        if new != path.read_text(encoding="utf-8"):
            stale.append(doc_id)
            if not args.check:
                path.write_text(new, encoding="utf-8")
                written += 1

    if args.check:
        if stale:
            print(f"{len(stale)} document(s) out of date with their extraction. Re-run:\n"
                  f"  python3 src/anchor_sections.py && python3 src/promote_full_text.py",
                  file=sys.stderr)
            for doc_id in stale[:10]:
                print(f"    {doc_id}", file=sys.stderr)
            return 1
        print(f"All {len(promote)} verbatim document(s) match their extraction; "
              f"{len(hold)} held back with content_exception.")
        return 0

    print(f"Wrote {written} document(s): {len(promote)} verbatim, {len(hold)} held back.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
