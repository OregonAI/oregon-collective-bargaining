#!/usr/bin/env python3
"""Ingest state-tier CBAs from the approved manifest: fetch, snapshot, hash, write
summary-mode documents under agreements/state/cba/.

  python3 src/ingest_cbas.py                    # tranche 1: every current-term state CBA
  python3 src/ingest_cbas.py --limit 3          # smoke run
  python3 src/ingest_cbas.py --only state-aee-association-of-engineering-employees-2025-2027
  python3 src/ingest_cbas.py --refetch          # ignore cached snapshots

TRANCHE 1 = family `cba` in _meta/sources/state.yml whose term BEGAN in or after the
roster term's start year (the current biennium plus the non-state units' odd terms).
Explicitly excluded, each with the reason printed:
  * the SEIU "Blackline" file — a redline, not the executed agreement (its manifest
    note says never ingest it as final text);
  * LOAs — separately-published letters are their own family and a later tranche;
  * history — predecessor terms come later, which is why `relationships.supersedes`
    is left EMPTY here rather than pointed at documents that do not exist yet. The
    successor chain is recorded when the predecessor lands, not faked before.

SUMMARY-FIRST, BY CONFIGURATION. schema.doc_types declares verbatim: false for both
types (the copyright gate in corpus.yml): a CBA is jointly authored with private
parties, and this corpus does not reproduce its text until the operator flips the
class. So documents carry `content_mode: summary`, NO '## Full text' section, and an
'## At a glance' built ONLY from facts with a named source:
  * the DAS filename and library listing        (title, term)
  * the LRU ratification chart, committed at _meta/state-roster-2025-2027.yml
                                                (unit, repr code, ratified date)
  * the fetched document itself                 (page count, stated term dates when a
                                                 dated span matching the term years is
                                                 found in the text; else omitted)
Nothing in the body paraphrases contract terms. The federal-reference phrasing rule
applies: a summary is never phrased as the requirement — here, never as the terms.

SNAPSHOTS follow oregon-audits: the PDF is fetched to _meta/snapshots/<id>.pdf
(gitignored, snapshot_policy: hash-only) and the pdftotext extraction is COMMITTED as
<id>.txt — hash_snapshot() then hashes the normalized extraction, which is what CI
re-verifies. A PDF whose extraction is under 200 chars (image-only scan) is SKIPPED
with a TODO line rather than ingested un-verifiable; none existed at first run.

References: ORS/OAR citations found in the extracted text land in
relationships.references_external as citation strings (resolved into ERF as up_cites
— cites, never implements). agency_registry_slugs is left empty: mapping bargaining
units to ERF agency slugs is crosswalk work with its own discipline (the audits
precedent), not a side effect of ingest.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from corpus_toolkit.repo import hash_snapshot           # noqa: E402

STATE_GROUP = REPO_ROOT / "_meta" / "sources" / "state.yml"
ROSTER_FILE = REPO_ROOT / "_meta" / "state-roster-2025-2027.yml"
SNAPSHOTS = REPO_ROOT / "_meta" / "snapshots"
OUT_DIR = REPO_ROOT / "agreements" / "state" / "cba"
UA = ("OregonAI-corpus-bot/0.1 (+https://github.com/OregonAI/oregon-collective-bargaining; "
      "civic corpus ingest)")
MIN_INTERVAL = 2.0

ORS = re.compile(r"ORS\s+(\d+[A-Z]?\.\d{3,})")
OAR = re.compile(r"OAR\s+(\d{3}-\d{3}-\d{4})")
# A dated span like "July 1, 2025 through June 30, 2027" (or "to"/"until"/"-").
DATESPAN = re.compile(r"([A-Z][a-z]+ \d{1,2},? \d{4})\s*(?:through|thru|to|until|[-–])\s*"
                      r"([A-Z][a-z]+ \d{1,2},? \d{4})")

_last_fetch = 0.0


def fetch(url: str, dest: Path, refetch: bool) -> None:
    global _last_fetch
    if dest.is_file() and not refetch:
        return
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=120).read()
    _last_fetch = time.monotonic()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"response is not a PDF ({data[:40]!r})")
    dest.write_bytes(data)


def extract(pdf: Path, txt: Path) -> tuple[str, int]:
    """(extracted text, page count) via poppler — the shared extractor stack."""
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True,
                   capture_output=True)
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True,
                          text=True).stdout
    pages = int(m.group(1)) if (m := re.search(r"^Pages:\s+(\d+)", info, re.M)) else 0
    return txt.read_text(encoding="utf-8", errors="replace"), pages


def roster_row(filename_title: str, roster: dict) -> dict | None:
    """The ratification-chart row for this file, via the roster's hand-recorded
    match/exclude substrings — the same semantics enumerate_cbas.py reconciles with,
    so ingest and enumeration cannot disagree about which unit a file is."""
    for section in ("state_contracts", "non_state_contracts"):
        for row in roster[section]:
            if row["match"] in filename_title and not (
                    row.get("exclude") and row["exclude"] in filename_title):
                return {**row, "non_state": section == "non_state_contracts"}
    return None


EXPIRE = re.compile(r"shall expire on\s+([A-Z][a-z]+ \d{1,2},?\s*\d{4})")


def _parse_date(s: str) -> str | None:
    try:
        return _dt.datetime.strptime(" ".join(s.replace(",", " ").split()),
                                     "%B %d %Y").date().isoformat()
    except ValueError:
        return None


def stated_term_dates(text: str, term: str) -> tuple[str | None, str | None]:
    """(effective, expiry) — ONLY what the document itself states, else None.

    Measured on the first fetches: these agreements make effectiveness CONDITIONAL
    ("upon ratification ... whichever is later"), so there is usually no effective
    date to extract and the field stays empty — an inferred one would be fabrication
    with a column name. Expiry IS stated plainly ("shall expire on June 30, 2027");
    it is taken only when its year equals the term's end year. A full dated span
    matching both term years, when present, supplies both."""
    y1, y2 = term.split("-")
    eff = exp = None
    for a, b in DATESPAN.findall(text):
        if a.split()[-1] == y1 and b.split()[-1] == y2:
            eff, exp = _parse_date(a), _parse_date(b)
            if eff and exp:
                break
            eff = exp = None
    if not exp:
        for d in EXPIRE.findall(text):
            if d.split()[-1] == y2 and (p := _parse_date(d)):
                exp = p
                break
    return eff, exp


def write_doc(rec: dict, row: dict | None, sha: str, pages: int, text: str,
              today: str) -> Path:
    doc_id, term, union = rec["id"], rec["term"], rec.get("union", "")
    title = rec["title"]
    refs = sorted({f"ORS {n}" for n in ORS.findall(text)} |
                  {f"OAR {n}" for n in OAR.findall(text)})
    eff, exp = stated_term_dates(text, term)

    fm: dict = {
        "schema_version": 1,
        "corpus": "oregon-collective-bargaining",
        "jurisdiction": "oregon",
        "id": doc_id,
        "title": title,
        "doc_type": "collective_bargaining_agreement",
        "citation": f"{term} {title.replace(term, '').strip()} agreement",
        "authority_level": "contract",
        "issuing_body": "State of Oregon (DAS Labor Relations Unit)",
        "union": union,
        "term": term,
        "effective_date": eff or "",
        "expiry_date": exp or "",
        "agency_registry_slugs": [],
        "source_url": rec["url"],
        "source_format": "pdf",
        "retrieved": today,
        "source_sha256": sha,
        "snapshot_policy": "hash-only",
        "status": "current",
        "content_mode": "summary",
        "reproduction_basis": ("jointly-authored contract; summary + official link per "
                               "the class determination in corpus.yml schema.doc_types "
                               "(verbatim: false)"),
        "conversion_notes": f"pdftotext -layout; {pages} pages, "
                            f"{len(text)} characters extracted; NOT human-verified",
        "last_verified": "",
        "verified_by": "",
        "maintainer": "@morficflux",
        "relationships": {
            "implements": [], "implemented_by": [],
            "references_external": refs,
            "related": [], "supersedes": [],
        },
        "tags": ["collective-bargaining", "state", "non-state-unit" if row and
                 row.get("non_state") else "state-workforce"],
    }

    glance = [f"Collective bargaining agreement between the State of Oregon (DAS Labor "
              f"Relations) and **{union or 'the signatory association'}** for the "
              f"**{term}** term."]
    if row:
        glance.append(f"- Bargaining unit (LRU chart): {row['unit']}"
                      + (f" — repr. code {row['repr']}" if row.get("repr") else ""))
        if row.get("ratified"):
            glance.append(f"- Ratified {row['ratified']} per the DAS LRU 2025-2027 "
                          f"bargaining chart (rev. 03/19/2026; committed at "
                          f"`_meta/state-roster-2025-2027.yml`)")
        if row.get("non_state"):
            glance.append("- A NON-STATE bargaining unit on the DAS chart: the workers "
                          "are not state employees; DAS bargains the agreement.")
        if row.get("note"):
            glance.append(f"- Chart note: {row['note']}")
    if eff:
        glance.append(f"- Effective date stated in the document's text: {eff}")
    if exp:
        glance.append(f"- Expiry stated in the document's text: {exp} (effectiveness is "
                      f"typically conditional on ratification and is recorded only when "
                      f"the document states a date)")
    glance.append(f"- Source document: {pages} pages (PDF, DAS CBA library)")

    body = f"""
> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: {rec['url']} (retrieved {today}).

# {title}

## At a glance

{chr(10).join(glance)}

This corpus is **summary-first for agreements**: the contract's text is not
reproduced here (see Curator notes), and nothing on this page states or
paraphrases the agreement's terms. Read the agreement itself at the official
source link above.

## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`): a CBA is jointly authored with private
parties, and "public record" and "freely reproducible" are not the same claim.
If the operator later flips the class, full text lands in a follow-up PR — the
committed snapshot extraction already carries what would be diffed.

Letters of agreement bound into this PDF by DAS are part of this source
snapshot; separately-published LOAs are their own documents in a later tranche.
The predecessor term's agreement is in the DAS library and is planned for the
history tranche — `supersedes` is recorded then, not faked now.

Extraction: {fm['conversion_notes']}.

## Cross-references

Statutes and rules the agreement's text cites are recorded in frontmatter
`relationships.references_external` ({len(refs)} citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
"""
    out = OUT_DIR / f"{doc_id}.md"
    out.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                                            width=88) + "---\n" + body,
                   encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only")
    ap.add_argument("--refetch", action="store_true")
    args = ap.parse_args()

    group = yaml.safe_load(STATE_GROUP.read_text(encoding="utf-8"))
    roster = yaml.safe_load(ROSTER_FILE.read_text(encoding="utf-8"))
    floor = roster["term"][:4]
    today = _dt.date.today().isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    picked, skipped = [], []
    for rec in group["sources"]:
        if args.only:
            if rec["id"] == args.only:
                picked.append(rec)
            continue
        if rec["family"] != "cba":
            continue
        if "blackline" in rec["id"]:
            skipped.append(f"{rec['id']}: redline, not the executed agreement")
            continue
        if not rec.get("term") or rec["term"][:4] < floor:
            continue
        picked.append(rec)
    if args.limit:
        picked = picked[:args.limit]

    ok = failed = 0
    for rec in picked:
        doc_id = rec["id"]
        pdf = SNAPSHOTS / f"{doc_id}.pdf"
        txt = SNAPSHOTS / f"{doc_id}.txt"
        try:
            fetch(rec["url"], pdf, args.refetch)
            text, pages = extract(pdf, txt)
            if len(text.strip()) < 200:
                skipped.append(f"{doc_id}: extraction under 200 chars (image-only scan?) "
                               f"— TODO: human verification / OCR pass required")
                txt.unlink(missing_ok=True)
                continue
            sha = hash_snapshot(doc_id, "pdf", SNAPSHOTS)
            row = roster_row(rec["title"], roster)
            out = write_doc(rec, row, sha, pages, text, today)
            print(f"ok  {out.relative_to(REPO_ROOT)}  ({pages}p, "
                  f"{'chart row matched' if row else 'NO chart row'})")
            ok += 1
        except Exception as e:                                   # noqa: BLE001
            print(f"FAIL {doc_id}: {e}", file=sys.stderr)
            failed += 1

    print(f"\ningested {ok}, failed {failed}, skipped {len(skipped)}")
    for s in skipped:
        print(f"  skipped: {s}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
