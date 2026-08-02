#!/usr/bin/env python3
"""Enumerate the DAS Labor Relations CBA library and write _meta/sources/state.yml.

  python3 src/enumerate_cbas.py            # rewrite the state source group
  python3 src/enumerate_cbas.py --check    # exit 1 if the group file would change (CI)

WHERE THE DATA ACTUALLY COMES FROM, because it is not the page a human would guess.

`oregon.gov/das/hr/pages/lru.aspx` renders no CBA links server-side. Its table is a
SharePoint list web part whose own configuration names the real source:

    "sharePointWebUrl": "/das/HR", "sharePointListUrl": "/das/HR/CBA",
    "sharePointViewName": "Collective Bargaining Agreements"

So enumeration reads the document library over REST — the same move
oregon-audits/src/enumerate_audits.py made against the SoS audits page:

    /das/HR/_api/web/GetFolderByServerRelativeUrl('/das/HR/CBA')/Files

Measured at first run (2026-08-02): 512 files in one unpaged response — the whole
history back to 2001, LOAs posted as separate files, terms in the filenames. The PDFs
themselves are plain static files; only the INDEX needed this route.

RECONCILIATION. _meta/state-roster-2025-2027.yml — the ratification chart, the tier's
coverage floor — is checked against the library every run. The check distinguishes:

  * roster row with a current-term file            -> covered
  * roster row ratified but current term not posted -> NAMED as posting lag, with the
    latest posted predecessor term. Measured at first run: SEIU master (only a
    "Blackline" redline posted), OLCC, OPDC x3, STEA — posting lags ratification at
    DAS by weeks-to-months, a fact about the publisher worth surfacing, not a bug.
  * roster row expected absent (unratified)        -> confirmed absent, or flagged if
    a file APPEARED (news!)
  * roster row matching NOTHING in any term        -> ABORT. The match patterns are
    hand-recorded; a total miss means the roster mapping or the enumeration broke,
    and a short manifest that looks fine is worse than no manifest.

Filename traps recorded so a re-enumeration does not rediscover them:
  1. Filenames are NOT derivable from the chart (chart "DHS SACU" vs filename
     "...Stabilization and Crisis Unit"; "IAFF KFFA Klamath Falls" vs "IAFF Kingsley
     Firefighters" — Kingsley Field is the Klamath Falls base; "OHA RN" vs "AFSCME
     OSH Registered Nurses"). The roster's `match` fields carry the mapping.
  2. "AFSCME DOC Security" is a PREFIX of "AFSCME DOC Security Plus" — the roster's
     `exclude` field exists for exactly this.
  3. One current file is named "SEIU 2025-2027 Blackline as of 02202026.pdf" — a
     redline, not the executed agreement. It is enumerated (it is in the library)
     with a note; ingestion must not treat it as the final text.
  4. LOAs are separate files whose names contain the word LOA but usually no term.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
GROUP_FILE = REPO_ROOT / "_meta" / "sources" / "state.yml"
ROSTER_FILE = REPO_ROOT / "_meta" / "state-roster-2025-2027.yml"

FILES_API = ("https://www.oregon.gov/das/HR/_api/web/"
             "GetFolderByServerRelativeUrl('/das/HR/CBA')/Files"
             "?$top=5000&$select=Name,ServerRelativeUrl,TimeLastModified,Length")
UA = ("OregonAI-corpus-bot/0.1 (+https://github.com/OregonAI/oregon-collective-bargaining; "
      "civic corpus ingest)")

TERM = re.compile(r"\b(20\d{2})\s*[-–]\s*(20\d{2})\b")
LOA = re.compile(r"\bloa\b|letter of agreement", re.I)
UNION_PREFIXES = ("AEE", "AFSCME", "AOCE", "CIA", "FOPPO", "IAFF", "ONA", "OPSA",
                  "OSEA", "OSPOA", "SEIU", "STEA")


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json;odata=nometadata"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def fetch_files() -> list[dict]:
    page = _get_json(FILES_API)
    files = page.get("value", [])
    # The Files endpoint returned everything unpaged at first run (512 < 5000). If the
    # library ever outgrows $top, silently missing the tail is the one unacceptable
    # outcome — the odata.nextLink shape differs between SP versions, so abort loudly
    # rather than half-follow it.
    if len(files) >= 5000 or "odata.nextLink" in page:
        sys.exit("ABORT: the Files response paged; enumeration would be incomplete. "
                 "Teach fetch_files() to follow this server's paging first.")
    return files


def slug(name: str) -> str:
    stem = re.sub(r"\.(pdf|docx)(\.pdf)?$", "", name, flags=re.I)
    s = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return f"state-{s}"


def union_of(name: str) -> str | None:
    if name.startswith("Oregon Nurses Association"):
        return "ONA"
    tok = name.split()[0]
    return tok if tok in UNION_PREFIXES else None


def build_sources(files: list[dict], today: str) -> list[dict]:
    out = []
    for f in sorted(files, key=lambda f: f["Name"].lower()):
        name = f["Name"]
        rec: dict = {
            "id": slug(name),
            "url": "https://www.oregon.gov" + urllib.parse.quote(f["ServerRelativeUrl"]),
            "family": "loa" if LOA.search(name) else "cba",
            "format": "pdf",
            "sha256": "",
            "title": re.sub(r"\.(pdf|docx)(\.pdf)?$", "", name, flags=re.I),
        }
        u = union_of(name)
        if u:
            rec["union"] = u
        m = TERM.search(name)
        if m:
            rec["term"] = f"{m.group(1)}-{m.group(2)}"
        rec["last_checked"] = today
        if "blackline" in name.lower():
            rec["notes"] = ("A blackline/redline, not the executed agreement. Do not "
                            "ingest as the final text of the term.")
        out.append(rec)
    return out


def reconcile(files: list[dict], roster: dict) -> tuple[list[str], list[str]]:
    """(report lines, fatal misses). Every roster row accounted for by name."""
    names = [f["Name"] for f in files]
    current_term = roster["term"].replace("-", "-")
    report, fatal = [], []
    for section in ("state_contracts", "non_state_contracts"):
        for row in roster[section]:
            hits = [n for n in names if row["match"] in n]
            if row.get("exclude"):
                hits = [n for n in hits if row["exclude"] not in n]
            terms = sorted({m.group(0).replace("–", "-").replace(" ", "")
                            for n in hits if (m := TERM.search(n))})
            if row.get("ratified") is None:
                report.append(f"EXPECTED-ABSENT confirmed: {row['unit']} (unratified)"
                              if not hits else
                              f"NEWS: {row['unit']} was expected absent (unratified on the "
                              f"chart) but the library now has: {hits}")
                continue
            if not hits:
                fatal.append(f"{row['unit']}: match {row['match']!r} found NOTHING in any term")
                continue
            # "Current" = a term that BEGAN with (or after) the roster term. Start-year,
            # not end-year: a 2023-2025 file ENDS in the roster's start year but expired
            # when the new term began, and counting it as coverage is exactly the
            # expired-served-as-current failure this corpus exists to prevent. Start-year
            # also handles the non-state units' non-biennial terms (2025-2026, 2025-2029).
            floor_year = current_term[:4]
            cur = [t for t in terms if t[:4] >= floor_year]
            if cur:
                report.append(f"covered: {row['unit']} ({', '.join(cur)})")
            else:
                latest = terms[-1] if terms else "no dated file"
                report.append(f"POSTING-LAG: {row['unit']} ratified {row['ratified']} but no "
                              f"current-term file; latest posted is {latest}")
    return report, fatal


def render(sources: list[dict], report: list[str], today: str) -> str:
    lag = sum(1 for r in report if r.startswith("POSTING-LAG"))
    head_lines = [
        "GENERATED by src/enumerate_cbas.py — do not hand-edit; re-run it.",
        "Human-approved via PR BEFORE any ingestion (review gate #1).",
        "",
        "The state tier's source group: every file in the DAS Labor Relations CBA",
        "library (/das/HR/CBA), enumerated over SharePoint REST because the index",
        "pages render nothing server-side. Whole history included — terms are in",
        "`term`; ingestion tranche 1 is the current term only. The coverage floor is",
        "_meta/state-roster-2025-2027.yml (the ratification chart); reconciliation",
        f"below is from the {today} run.",
        "",
        f"RECONCILIATION ({lag} posting lag(s)):",
        *[f"  {line}" for line in report],
    ]
    doc = {
        "group": "state",
        "title": "State of Oregon — DAS Labor Relations CBA library",
        "employer": "state",
        "crawl": {
            "decision": "proceed",
            "checked": "2026-08-02",
            "basis": ("oregon.gov robots.txt fetched and read in full at survey time: no "
                      "disallow on /das/HR/CBA/ or /das/HR/Documents/ (the only DAS rule "
                      "is an unrelated survey page). Honest UA; the REST endpoint and the "
                      "PDFs both answer it with 200."),
            "hosts": [{
                "host": "www.oregon.gov",
                "robots_url": "https://www.oregon.gov/robots.txt",
                "ai_block": False,
                "content_signal": None,
                "notes": ("State enterprise portal. The CBA index is a client-side "
                          "SharePoint web part; enumeration uses the REST Files endpoint "
                          "its own config names. Documents are plain static PDFs."),
            }],
        },
        "last_checked": today,
        "upstream_signal": (
            "Fully enumerable — the one publisher in this corpus with a real change "
            "feed: re-run the REST enumeration and diff the file set; per-file "
            "TimeLastModified is served, and DAS overwrites files in place rarely "
            "(new terms get new filenames). Posting lags ratification by weeks to "
            "months (measured: 6 ratified 2025-2027 contracts not yet posted at first "
            "enumeration), so absence of a current-term file weeks after ratification "
            "is normal, and the roster reconciliation names each case."),
        "sources": sources,
    }
    body = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
    return "".join(f"# {l}\n" if l else "#\n" for l in head_lines) + body


def _strip_dates(text: str) -> str:
    """--check comparison ignores pure re-dating: last_checked moves on every run by
    design, and a diff that is ONLY dates is not drift."""
    return re.sub(r"^(\s*(?:#.*)?last_checked:).*$|^#.*\d{4}-\d{2}-\d{2} run.*$", r"\1",
                  text, flags=re.M)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed group file is not what enumeration produces")
    args = ap.parse_args()

    roster = yaml.safe_load(ROSTER_FILE.read_text(encoding="utf-8"))
    files = fetch_files()
    today = _dt.date.today().isoformat()
    sources = build_sources(files, today)
    report, fatal = reconcile(files, roster)

    print(f"library files: {len(files)}   sources: {len(sources)}   "
          f"cba: {sum(1 for s in sources if s['family'] == 'cba')}   "
          f"loa: {sum(1 for s in sources if s['family'] == 'loa')}")
    for line in report:
        print(" ", line)

    if fatal:
        for line in fatal:
            print(f"\nABORT: {line}", file=sys.stderr)
        print("Roster reconciliation failed; the group file was NOT written.", file=sys.stderr)
        return 1

    text = render(sources, report, today)
    if args.check:
        current = GROUP_FILE.read_text(encoding="utf-8") if GROUP_FILE.is_file() else ""
        if _strip_dates(current) != _strip_dates(text):
            print("\n_meta/sources/state.yml is STALE — re-run src/enumerate_cbas.py",
                  file=sys.stderr)
            return 1
        print("_meta/sources/state.yml is current.")
        return 0

    GROUP_FILE.write_text(text, encoding="utf-8")
    print(f"wrote {GROUP_FILE.relative_to(REPO_ROOT)}: {len(sources)} source(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
