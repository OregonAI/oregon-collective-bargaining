#!/usr/bin/env python3
"""One-off: ingest Marion's MCDAA and MCJEA successor agreements as new documents,
and mark the predecessors each supersedes `status: superseded` without touching
their committed text, hash, or `retrieved` date (oregon-collective-bargaining#63).

  python3 src/ingest_marion_successors.py            # fetch, ingest, supersede
  python3 src/ingest_marion_successors.py --check    # report the plan, write nothing

WHY THIS IS NOT A RE-RUN OF `src/ingest_counties.py`. That ingester's doc_id is
derived mechanically from the source manifest id (`marion-mcdaa-cba` ->
`marion-county-mcdaa-cba`), and `_meta/sources/marion.yml` is itself GENERATED
from an archived survey fetch (`src/discover_counties.py`) -- re-running it does
not, and must not, invent a new id for a successor at the SAME undated, overwritten-
in-place URL (AGENTS.md's hashing-everywhere rule exists for exactly this county).
Per AGENTS.md rule 3 ("a successor records `supersedes`; a superseded agreement
STAYS, marked `status: superseded`"), the right id for the new document carries its
OWN term, and the committed predecessor is never replaced in place.

So this script: fetches the live PDF at the SAME manifest URL (the stable URL now
serves the successor text -- verified against the committed predecessor's own text
before this script was written, not assumed from the manifest's stale `sha256`,
which this script never reads or writes: that baseline is `corpus-detect-changes
--record-baseline`'s field to fill, and per the issue's operator decision it is left
for the reviewer to accept here, not recorded by this run). It reuses
`ingest_counties.write_doc` for the new document (the same verbatim-or-stub
metadata logic as every other county document), under an EXPLICIT id this script
provides rather than one derived from the manifest, then stamps
`relationships.supersedes` on the new document and flips `status` on the
predecessor -- both via targeted line edits (`set_field`'s discipline in
src/anchor_sections.py: "a YAML re-dump never runs here; hand formatting must
survive"), never a full YAML re-dump of either file.

After this script: `src/anchor_sections.py` then `src/promote_full_text.py` turn
the new document's committed extraction into its `## Full text` section and
recompute its `source_sha256` from the anchored snapshot, exactly as for every
other verbatim document in this corpus.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import ingest_counties  # noqa: E402

SOURCES_DIR = REPO_ROOT / "_meta" / "sources"
SNAPSHOTS = REPO_ROOT / "_meta" / "snapshots"
AGREEMENTS = REPO_ROOT / "agreements"
EMPLOYERS = REPO_ROOT / "_meta" / "employers.yml"

# (predecessor doc_id, successor doc_id, source manifest id, term, title)
SUCCESSIONS = [
    dict(old_id="marion-county-mcdaa-cba", new_id="marion-county-mcdaa-cba-2026-2029",
         source_id="marion-mcdaa-cba", term="2026-2029", title="MCDAA CBA"),
    dict(old_id="marion-county-mcjea-cba", new_id="marion-county-mcjea-cba-2026-2028",
         source_id="marion-mcjea-cba", term="2026-2028", title="MCJEA CBA"),
]


# -- targeted frontmatter edits (never a YAML re-dump -- see module docstring) ----

def set_supersedes(text: str, ids: list[str]) -> str:
    """Fill `relationships.supersedes` with `ids` (sorted), replacing either an
    empty `[]` or a previously-set list. Raises if the field is not found, so a
    regex that silently matched nothing never passes as a successful edit."""
    block = "  supersedes:\n" + "".join(f"  - {i}\n" for i in sorted(set(ids)))
    pattern = re.compile(r"^  supersedes:\s*(?:\[\])?\n(?:  - .+\n)*", re.M)
    new_text, n = pattern.subn(block, text, count=1)
    if n == 0:
        raise ValueError("no relationships.supersedes field found")
    return new_text


def flip_status(text: str, new_status: str) -> str:
    """Rewrite the top-level `status:` line only -- term, dates, hash, retrieved,
    and the body (including any committed `## Full text`) are untouched."""
    new_text, n = re.subn(r"^status:.*$", f"status: {new_status}", text, count=1,
                          flags=re.M)
    if n == 0:
        raise ValueError("no status field found")
    return new_text


def add_supersession_note(text: str, note: str) -> str:
    """Insert `note` as the first line of `## Curator notes`, ahead of whatever
    curator prose was already there."""
    heading = "## Curator notes\n\n"
    idx = text.find(heading)
    if idx == -1:
        raise ValueError("no '## Curator notes' heading found")
    insert_at = idx + len(heading)
    return text[:insert_at] + note + "\n\n" + text[insert_at:]


def supersede_predecessor(old_id: str, new_id: str, term: str, *, check: bool = False) -> bool:
    """Mark the committed predecessor `status: superseded`, record the successor in
    a curator note, and leave everything else -- text, hash, retrieved, supersedes
    of its own -- exactly as committed. Returns whether a write happened (or, under
    `check`, would have)."""
    path = next((p for p in AGREEMENTS.rglob(f"{old_id}.md")), None)
    if path is None:
        raise FileNotFoundError(f"no committed document for {old_id!r}")
    text = path.read_text(encoding="utf-8")
    if re.search(r"^status: superseded$", text, re.M):
        return False   # already done -- idempotent re-run
    out = flip_status(text, "superseded")
    out = add_supersession_note(
        out, f"**Superseded by `{new_id}`** ({term} term), a successor agreement at "
             f"this same stable URL. This document's text and hash are unchanged; "
             f"the county's own index may no longer list it.")
    if not check:
        path.write_text(out, encoding="utf-8")
    return True


def ingest_successor(succ: dict, county: dict, *, refetch: bool = False,
                     check: bool = False) -> Path | None:
    """Fetch and ingest one successor agreement under its own, explicit `new_id`
    (never the manifest-derived id `ingest_counties.main` would compute), then stamp
    `relationships.supersedes` on the written document."""
    group = yaml.safe_load((SOURCES_DIR / "marion.yml").read_text(encoding="utf-8"))
    rec = next(s for s in group["sources"] if s["id"] == succ["source_id"])
    new_id = succ["new_id"]
    pdf = SNAPSHOTS / f"{new_id}.pdf"
    txt = SNAPSHOTS / f"{new_id}.txt"
    if check:
        state = "would fetch and ingest" if not pdf.is_file() or refetch else "cached, would reuse"
        print(f"  {new_id}: {state}; supersedes {succ['old_id']}")
        return None
    data, fresh = ingest_counties.fetch(rec["url"], pdf, refetch)
    text, pages = ingest_counties.extract(pdf, txt)
    sha = ingest_counties.hash_snapshot(new_id, "pdf", SNAPSHOTS)
    out = ingest_counties.write_doc(
        county, {**rec, "term": succ["term"], "title": succ["title"]}, new_id, sha,
        pages, text, _today(), {}, rec["url"], fresh=fresh)
    marked = out.read_text(encoding="utf-8")
    out.write_text(set_supersedes(marked, [succ["old_id"]]), encoding="utf-8")
    return out


def _today() -> str:
    import datetime as _dt
    return _dt.date.today().isoformat()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="report the plan; fetch, write, and edit nothing")
    args = ap.parse_args()

    employers = {e["slug"]: e for e in
                 yaml.safe_load(EMPLOYERS.read_text(encoding="utf-8"))["employers"]}
    county = employers["marion-county"]

    for succ in SUCCESSIONS:
        ingest_successor(succ, county, refetch=args.refetch, check=args.check)
        if args.check:
            print(f"  {succ['old_id']}: would mark status: superseded")
        else:
            wrote = supersede_predecessor(succ["old_id"], succ["new_id"], succ["term"])
            print(f"{'superseded' if wrote else 'already superseded'}: {succ['old_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
