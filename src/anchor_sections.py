#!/usr/bin/env python3
"""Insert `### ` article anchors into the big agreement extractions.

  python3 src/anchor_sections.py            # anchor snapshots in place
  python3 src/anchor_sections.py --check    # exit 1 if any anchor is stale (CI)
  python3 src/anchor_sections.py --report   # per-file anchor counts, write nothing

WHY ANCHORS. A collective bargaining agreement is read one article at a time --
"what is the grievance procedure", "how is overtime computed" -- and after the
verbatim flip the bodies are the real thing: the SEIU master alone is 1.33 MB,
26x the toolkit's BIG_DOC_BYTES gate. Without anchors `get_document` on one of
these is a glance-or-everything binary. Toolkit >= v1.21.0 serves `### `
subsections and lists them on big-doc responses, so the fix is anchors in the
text rather than splitting one agreement into many documents: an article is not
a free-standing instrument, it is a clause of a contract that is negotiated,
ratified and superseded as ONE thing. Splitting would invent 6,914 documents
that no citation scheme, no drift check and no supersession edge can address.

MECHANICS. Anchoring PREFIXES an existing heading line with `### `. It never
adds, removes, or reorders a word. That is what keeps provenance passing: the
verifier requires every non-empty line of `## Full text` to appear in the
snapshot IN ORDER, so the anchors must live in BOTH the snapshot and the
document body. They do -- promote_full_text.py copies the anchored snapshot.
Re-running is a no-op (an already-anchored line is never re-anchored), which is
what makes --check meaningful.

Anchoring CHANGES `source_sha256`, because the recorded hash for a hash-only doc
with a committed .txt is sha256 of the normalized snapshot text. That is not a
side effect to paper over -- promote_full_text.py recomputes it, and this script
deliberately does not, so that the hash is only ever written by the same pass
that writes the body it describes.

THE TABLE OF CONTENTS IS THE TRAP, and it is why this is not a one-line regex.
Measured on the SEIU master: 470 lines match `^ARTICLE`, but only 309 are
article headings. The first 161 are the TOC -- and that TOC is TWO-COLUMN, so a
single line carries two article references and wraps mid-title:

    'ARTICLE 1--PARTIES TO THE AGREEMENT.......... 1      ARTICLE 22T--NO DISCRIMINATION .. 20'
    'ARTICLE 10.2--UNION ORGANIZER VISITATIONS (Institutions'      <- no dot leaders at all

Filtering on dot leaders alone leaves 39 wrapped continuations behind, and each
false anchor is worse than a missing one: `### ARTICLE 5` landing on a TOC entry
means a subsection request returns a page number instead of the article. So the
TOC is excluded STRUCTURALLY -- find where the dot-leader region ends, anchor
only after it -- with the dot-leader test kept as a second filter.

PER-CORPUS GRAIN, measured before being written (2026-08-03), over the 141
snapshots above the gate:

    ARTICLE <n>     130 files, 6,914 headings   <- the grain used
    Section <n>     104 files, 19,331 headings  <- rejected: 186/file fragments
                                                   articles into sub-clauses
    APPENDIX         79 files,   239 headings   <- anchored, same rule
    LETTER OF AGR    65 files, 1,205 headings   <- anchored: DAS binds LOAs into
                                                   the master PDF, and they are
                                                   what mid-term questions hit

Six big files carry no ARTICLE grain at all. Four are unusable extractions that
promote_full_text.py holds back entirely (see its EXCLUSIONS); the remaining two
number their articles differently and are matched by the `<n>. TITLE` rule.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extraction_quality  # noqa: E402  (sibling module, same directory)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "_meta" / "snapshots"

# Matches the toolkit's big-doc threshold. Anchoring a document the server will
# never call "big" adds noise to text nobody needs to navigate.
BIG_DOC_BYTES = 50 * 1024

ANCHOR = "### "

# A run of leaders is the table-of-contents signature across every publisher here.
DOT_LEADER = re.compile(r"\.{4,}|\. \. \. \.|…{2,}")

# Heading forms. Each was measured to occur as a real heading in these extractions;
# none is a prose form.
#
# LEADING WHITESPACE IS UNBOUNDED ON PURPOSE. `pdftotext -layout` preserves the
# page's visual layout, and every publisher here CENTERS its article headings --
# so the real heading arrives as 30-odd spaces then the word. An earlier cap of 8
# was measured to miss the body headings of 14 large agreements (Teamsters,
# Yamhill SHERIFF, Coos AFSCME and others) while still matching their TOC lines,
# which are flush left. It anchored the table of contents and nothing else: the
# precise inversion of what this script is for. The guards against sweeping up
# indented prose are the length cap and the dot-leader filter below, not indent.
# WHAT FOLLOWS THE NUMBER IS THE DISCRIMINATOR, not the word "ARTICLE". Because
# `pdftotext -layout` wraps paragraphs, a sentence like "...as provided in Article
# 33 shall be retroactive" begins a line with `Article 33`, indistinguishable from
# a heading by prefix alone. Measured: matching on the prefix produced 152 such
# false anchors corpus-wide. A heading is followed by a TITLE -- a separator then
# an uppercase word; prose is followed by a lowercase word, a comma, or nothing.
# Case matters here, so these patterns are deliberately NOT re.I.
_ART_NUM = r"[0-9IVXLC][0-9A-Za-z.]*"
# Benton's ONA agreement is a line-numbered legal document: every line carries a
# gutter number, so its headings arrive as `    1        ARTICLE 3 - MANAGEMENT
# RIGHTS`. Without this the whole 203 KB agreement -- the only one left unanchored
# after the grain survey -- gets no navigation at all. The gutter digit stays in the
# anchor text (`### 1    ARTICLE 3 - ...`) because it is in the committed extraction
# and this script does not delete words; the label is uglier, the text is honest.
_GUTTER = r"(?:\d{1,3}\s+)?"
HEADING_PATTERNS = [
    # ARTICLE 1--PARTIES / Article 1 - Recognition / Article 10.1M--Union Rights /
    # Article 22 & 22T--No Discrimination. Separator (or plain space) then a title.
    re.compile(rf"^\s*{_GUTTER}(?:ARTICLE|Article)\s+{_ART_NUM}"
               rf"(?:\s*[-–—:]{{1,3}}\s*|\s+)(?=[A-Z&])"),
    # A standalone all-caps `ARTICLE 5` on its own line. Restricted to uppercase and
    # barred from a trailing period so that the prose sentence `Article 12.` -- which
    # is otherwise the same shape -- is not swept up.
    re.compile(rf"^\s*ARTICLE\s+[0-9IVXLC][0-9A-Z]*\s*$"),
    # APPENDIX A - LETTERS OF AGREEMENT. Same title requirement, same reason.
    re.compile(r"^\s*(?:APPENDIX|Appendix)\s+[0-9A-Z][0-9A-Za-z.]*(?:\s*[-–—:]{1,3}\s*|\s+)(?=[A-Z])"),
    re.compile(r"^\s*APPENDIX\s+[0-9A-Z][0-9A-Z]*\s*$"),
    # LETTER OF AGREEMENT / MEMORANDUM OF UNDERSTANDING bound into the same PDF.
    # DAS binds LOAs into the master agreement, and they are what mid-term
    # questions land on, so they get anchors of their own.
    #
    # The negative lookahead is the same lesson as the article rule: these phrases
    # are also how the body REFERS to those instruments ("This Letter of Agreement
    # will sunset on June 30, 2027"), so a lowercase word after the phrase means a
    # sentence, not a heading. A real one is bare, numbered, or `: Titled`.
    re.compile(r"^\s*(?:LETTER OF AGREEMENT|MEMORANDUM OF (?:UNDERSTANDING|AGREEMENT))"
               r"(?!\s+[a-z])", re.I),
    # `12.  RECOGNITION` -- the Deschutes/Benton numbering, uppercase title required
    # so that ordinary numbered list items in prose are not swept up.
    re.compile(r"^\s*\d{1,2}\.\s{2,}[A-Z][A-Z '&/\-]{3,}$"),
]

# A heading is short. This is the guard against a paragraph that happens to begin
# with the word "Article", which prose does ("Article 12 provides that ...").
MAX_HEADING_CHARS = 120


# A heading does not end in sentence punctuation. Kept deliberately narrow: the
# title requirement in HEADING_PATTERNS already rejects prose, so this only has to
# catch a sentence whose wrap happens to LOOK like a title. It must not reject a
# closing parenthesis -- `ARTICLE 45.5W--FILLING OF VACANCIES (Licensing Boards)`
# is a real heading, and an earlier version that barred `)` dropped it.
PROSE_TAIL = re.compile(r"[,;]$|\.$")


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > MAX_HEADING_CHARS:
        return False
    if DOT_LEADER.search(line):
        return False
    if PROSE_TAIL.search(stripped):
        return False
    return any(p.match(line) for p in HEADING_PATTERNS)


def toc_end(lines: list[str]) -> int:
    """Index after the table-of-contents region, or 0 if there is none.

    The TOC is the run of dot-leader lines near the front of the document. We take
    the LAST such line, but only if it sits in the front quarter of the file --
    otherwise a stray leader in an appendix table would swallow the whole body and
    silently anchor nothing, which is exactly the kind of quiet no-op this
    platform keeps producing.
    """
    limit = max(40, len(lines) // 4)
    last = 0
    for i, line in enumerate(lines[:limit]):
        if DOT_LEADER.search(line):
            last = i
    return last + 1 if last else 0


def anchor_text(text: str) -> tuple[str, int]:
    """Return (anchored text, number of anchors added). Idempotent."""
    lines = text.splitlines(keepends=True)
    start = toc_end([l.rstrip("\n") for l in lines])
    added = 0
    out = []
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        eol = raw[len(line):]
        if i >= start and not line.lstrip().startswith(ANCHOR.strip()) and is_heading(line):
            # Prefix, preserving the original line verbatim after the anchor so the
            # word sequence is untouched.
            out.append(f"{ANCHOR}{line.strip()}{eol}")
            added += 1
        else:
            out.append(raw)
    return "".join(out), added


def targets() -> list[pathlib.Path]:
    """Big snapshots that are actually publishable text.

    Unusable extractions are skipped rather than anchored, because anchoring one is
    meaningless work on bytes that will never reach a document body -- and on the
    raw-PDF case it is worse than meaningless: the binary happens to contain the
    literal bytes `### `, so a prefix pass there is not provably word-preserving.
    src/extraction_quality.py owns that judgement; this file does not duplicate it.
    """
    unusable = set(extraction_quality.audit())
    out = []
    for p in sorted(SNAPSHOTS.glob("*.txt")):
        if p.stat().st_size <= BIG_DOC_BYTES:
            continue
        if p.stem in unusable:
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any snapshot would gain an anchor")
    ap.add_argument("--report", action="store_true",
                    help="print per-file anchor counts and write nothing")
    args = ap.parse_args()

    stale, total, touched = [], 0, 0
    for path in targets():
        text = path.read_text(encoding="utf-8", errors="replace")
        new, added = anchor_text(text)
        existing = text.count(f"\n{ANCHOR}") + int(text.startswith(ANCHOR))
        total += added
        if args.report:
            if added or existing:
                print(f"  {added:5d} new  {existing:5d} existing  {path.name[:70]}")
            continue
        if added:
            stale.append((path.name, added))
            if not args.check:
                path.write_text(new, encoding="utf-8")
                touched += 1

    if args.report:
        print(f"\n{total} anchors would be added across {len(targets())} snapshots")
        return 0
    if args.check:
        if stale:
            print(f"{len(stale)} snapshot(s) missing anchors "
                  f"({sum(n for _, n in stale)} total). Re-run:\n"
                  f"  python3 src/anchor_sections.py", file=sys.stderr)
            for name, n in stale[:10]:
                print(f"    {n:5d}  {name}", file=sys.stderr)
            return 1
        print(f"All {len(targets())} big snapshots are anchored.")
        return 0

    print(f"Anchored {total} heading(s) across {touched} snapshot(s).")
    print("source_sha256 is now stale -- run src/promote_full_text.py to rewrite "
          "bodies and hashes together.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
