#!/usr/bin/env python3
"""Ingest county-tier agreements from the approved source groups: fetch, snapshot,
hash, write summary-mode documents under agreements/<employer>/{cba,loa}/.

  python3 src/ingest_counties.py                 # every county group
  python3 src/ingest_counties.py --only multnomah
  python3 src/ingest_counties.py --limit 3       # first N sources per county (smoke)
  python3 src/ingest_counties.py --refetch

SAME DISCIPLINE AS THE STATE TIER (src/ingest_cbas.py), different publisher shapes:

  * Documents land at agreements/<employer-slug>/{cba,loa}/<doc_id>.md with
    doc_id = the source id re-prefixed with the registry slug (multnomah-... ->
    multnomah-county-...), so the citation resolver's employer filter and the
    scoped root's registry validation agree.
  * `status: current` for every county document, and the basis is recorded here:
    each source sits on the county's OWN operative labor-agreements index page
    (the archived fetch in _meta/discovery/ is the evidence). County pages,
    unlike the DAS library, do not publish history.
  * TERMS: where the index stated no term (Clackamas shows none; Lane and Marion
    serve undated filenames), the document's OWN text is searched — a dated span
    or a "shall expire on" clause near the front — and anything not found stays
    empty. An inferred term would be fabrication with a column name.
  * CLACKAMAS HTML SOURCES: measured at ingest, the "intermediate pages" are not
    intermediate — Clackamas publishes each agreement/MOA's FULL TEXT as the HTML
    page itself (the FOPPO page opens with the preamble). So: if the page links a
    dochub document, that PDF is the source; otherwise the PAGE IS THE DOCUMENT —
    snapshotted as .html, main-content text extracted and committed as .txt,
    `source_format: html`. A page with neither a document link nor extractable
    body text is a TODO skip, never a guess.
  * LOAs/MOUs are letter_of_agreement docs under loa/, `related`-linked to the
    county's matching-union CBA when exactly one matches — ambiguity gets no link.

State-library LOAs remain deferred (recorded in the CHANGELOG): they are mostly
undated and span decades, so their currency needs a per-document curation pass,
not a mechanical status: current.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from corpus_toolkit.repo import hash_snapshot           # noqa: E402

SOURCES_DIR = REPO_ROOT / "_meta" / "sources"
EMPLOYERS = REPO_ROOT / "_meta" / "employers.yml"
SNAPSHOTS = REPO_ROOT / "_meta" / "snapshots"
AGREEMENTS = REPO_ROOT / "agreements"
UA = ("OregonAI-corpus-bot/0.1 (+https://github.com/OregonAI/oregon-collective-bargaining; "
      "civic corpus ingest)")
MIN_INTERVAL = 2.0

ORS = re.compile(r"ORS\s+(\d+[A-Z]?\.\d{3,})")
OAR = re.compile(r"OAR\s+(\d{3}-\d{3}-\d{4})")
DATESPAN = re.compile(r"([A-Z][a-z]+ \d{1,2},?\s*\d{4})\s*(?:through|thru|to|until|[-–])\s*"
                      r"([A-Z][a-z]+ \d{1,2},?\s*\d{4})")
EXPIRE = re.compile(r"(?:shall\s+)?expires?\s+(?:on\s+)?([A-Z][a-z]+ \d{1,2},?\s*\d{4})")
DOCHUB = re.compile(r'href="(https://dochub\.clackamas\.us/documents/drupal/[^"]+)"')
UNION_TOKENS = ("AFSCME", "SEIU", "ONA", "FOPPO", "IBEW", "IUOE", "Teamsters",
                "Operating Engineers", "Oregon Nurses", "CCPOA", "CCEA", "WCPOA",
                "WCPAA", "MCEA", "MCLEA", "MCDAA", "MCJEA", "MCSSA", "JCSEA", "YCEA",
                "YCSO", "YCDDAA", "YCJDWA", "DCSEA", "DCDAA", "LCPOA", "CADS",
                "CCDSA", "CCSA", "IAFF", "Painters", "Pharmacists", "Prosecuting",
                "Local 626", "Local 88")

_last_by_host: dict[str, float] = {}


def fetch(url: str, dest: Path | None, refetch: bool, expect_pdf: bool = True) -> bytes:
    if dest and dest.is_file() and not refetch:
        return dest.read_bytes()
    host = urllib.parse.urlparse(url).netloc
    wait = MIN_INTERVAL - (time.monotonic() - _last_by_host.get(host, 0.0))
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=120).read()
    _last_by_host[host] = time.monotonic()
    if expect_pdf and not data.startswith(b"%PDF"):
        raise ValueError(f"response is not a PDF ({data[:40]!r})")
    if dest:
        dest.write_bytes(data)
    return data


def extract(pdf: Path, txt: Path) -> tuple[str, int]:
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True,
                   capture_output=True)
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True,
                          text=True).stdout
    pages = int(m.group(1)) if (m := re.search(r"^Pages:\s+(\d+)", info, re.M)) else 0
    return txt.read_text(encoding="utf-8", errors="replace"), pages


def _parse_date(s: str) -> str | None:
    try:
        return _dt.datetime.strptime(" ".join(s.replace(",", " ").split()),
                                     "%B %d %Y").date().isoformat()
    except ValueError:
        return None


def own_dates(text: str, known_term: str | None) -> tuple[str | None, str | None, str | None]:
    """(term, effective, expiry) from the document's own text, front-of-document only
    (the term clause lives in the preamble or the duration article near the end, but a
    front-scoped span avoids matching grievance-timeline examples). Years are sanity-
    bounded; nothing found stays None. If a term was already known from the index, only
    a span AGREEING with it fills the dates — a conflicting span is reported, not used."""
    head = text[:12000]
    for a, b in DATESPAN.findall(head):
        fa, fb = _parse_date(a), _parse_date(b)
        if not (fa and fb) or not (fa < fb) or not ("1990" <= fa[:4] <= "2040"):
            continue
        span_term = f"{fa[:4]}-{fb[:4]}"
        if known_term and span_term != known_term:
            continue
        return span_term, fa, fb
    for d in EXPIRE.findall(head):
        fd = _parse_date(d)
        if fd and "1990" <= fd[:4] <= "2040" and (
                not known_term or fd[:4] == known_term[5:]):
            return known_term, None, fd
    if not known_term:
        # Year-only span near the front ("2022 – 2025 agreement") — enough for `term`,
        # not for dates.
        if (m := re.search(r"\b(20\d{2})\s*[–-]\s*(20\d{2})\b", head)) and m.group(1) < m.group(2):
            return f"{m.group(1)}-{m.group(2)}", None, None
    return known_term, None, None


def union_of(title: str) -> str:
    for tok in UNION_TOKENS:
        if re.search(rf"\b{re.escape(tok)}\b", title, re.I):
            return tok
    return ""


def html_source(url: str, refetch: bool) -> tuple[str | None, str | None]:
    """(dochub_pdf_url, page_html) for a Clackamas HTML source: a linked document
    wins; otherwise the page itself is the document."""
    page = fetch(url, None, refetch, expect_pdf=False).decode("utf-8", errors="replace")
    links = DOCHUB.findall(page)
    return (links[0] if links else None), page


def html_main_text(page: str) -> str:
    """The page's main-content text — the agreement text Clackamas publishes inline."""
    m = re.search(r"<main.*?</main>", page, re.S)
    body = m.group(0) if m else page
    body = re.sub(r"<(script|style|nav|header|footer).*?</\1>", " ", body, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    return "\n".join(" ".join(l.split()) for l in re.split(r"\s{2,}|\n", text) if l.strip())


def write_doc(county: dict, rec: dict, doc_id: str, sha: str, pages: int, text: str,
              today: str, cba_by_union: dict, fetched_url: str,
              src_fmt: str = "pdf") -> Path:
    family = rec["family"]
    title = rec["title"]
    union = union_of(title)
    term, eff, exp = own_dates(text, rec.get("term"))
    refs = sorted({f"ORS {n}" for n in ORS.findall(text)} |
                  {f"OAR {n}" for n in OAR.findall(text)})

    related = []
    if family == "loa" and union and len(cba_by_union.get(union, [])) == 1:
        related = list(cba_by_union[union])

    kind = ("letter_of_agreement" if family == "loa"
            else "collective_bargaining_agreement")
    cite_bits = [term, county["name"], union or title, "agreement" if family == "cba"
                 else "letter of agreement"]
    fm: dict = {
        "schema_version": 1,
        "corpus": "oregon-collective-bargaining",
        "jurisdiction": county["jurisdiction"],
        "id": doc_id,
        "title": f"{county['name']} — {title}",
        "doc_type": kind,
        "citation": " ".join(b for b in cite_bits if b),
        "authority_level": "contract",
        "issuing_body": county["name"],
        "union": union,
        "term": term or "",
        "effective_date": eff or "",
        "expiry_date": exp or "",
        "agency_registry_slugs": [],
        "source_url": rec["url"],
        "source_format": src_fmt,
        "retrieved": today,
        "source_sha256": sha,
        "snapshot_policy": "hash-only",
        "status": "current",
        "content_mode": "summary",
        "reproduction_basis": ("jointly-authored contract; summary + official link per "
                               "the class determination in corpus.yml schema.doc_types "
                               "(verbatim: false)"),
        "conversion_notes": (f"pdftotext -layout; {pages} pages, "
                             f"{len(text)} characters extracted; NOT human-verified"
                             if src_fmt == "pdf" else
                             f"main-content text of the county's HTML page; "
                             f"{len(text)} characters extracted; NOT human-verified"),
        "last_verified": "",
        "verified_by": "",
        "maintainer": "@morficflux",
        "relationships": {
            "implements": [], "implemented_by": [],
            "references_external": refs,
            "related": related, "supersedes": [],
        },
        "tags": ["collective-bargaining", "county", county["slug"]],
    }

    glance = [f"{'Letter of agreement / MOU under' if family == 'loa' else 'Collective bargaining agreement between'} "
              f"**{county['name']}** and **{union or 'the signatory association'}**"
              + (f" — **{term}** term." if term else ".")]
    glance.append(f"- Listed on the county's labor agreements index as: “{title}”"
                  f" (index archived in `_meta/discovery/`)")
    if eff:
        glance.append(f"- Effective date stated in the document's text: {eff}")
    if exp:
        glance.append(f"- Expiry stated in the document's text: {exp}")
    if not term:
        glance.append("- No term is stated on the index or found in the document's "
                      "front matter — `term` is left empty rather than inferred; the "
                      "county presents this as its operative agreement")
    glance.append(f"- Source document: {pages} pages (PDF)" if src_fmt == "pdf" else
                  "- Source document: an HTML page — the county publishes this "
                  "instrument's text inline rather than as a PDF")
    if fetched_url != rec["url"]:
        glance.append(f"- Fetched via the county's document CDN: {fetched_url} "
                      f"(the index links an intermediate page; see Curator notes)")

    src_note = rec.get("notes")
    body = f"""
> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: {rec['url']} (retrieved {today}).

# {fm['title']}

## At a glance

{chr(10).join(glance)}

This corpus is **summary-first for agreements**: the contract's text is not
reproduced here (see Curator notes), and nothing on this page states or
paraphrases the agreement's terms. Read the agreement itself at the official
source link above.

## Curator notes

Summary-first is the recorded class determination (`corpus.yml
schema.doc_types`, `verbatim: false`). `status: current` records that this
document sits on the county's own operative labor-agreements index at ingest
time — county pages, unlike the DAS library, publish no history, so currency
rests on the index and on content-hash drift detection.
{f"Source-manifest note: {src_note}" if src_note else ""}
Extraction: {fm['conversion_notes']}.

## Cross-references

Statutes and rules the document's text cites are recorded in frontmatter
`relationships.references_external` ({len(refs)} citation(s)) and resolve into
`executive-regulatory-frameworks` as cites — this corpus asserts no
`implements` edge anywhere.
"""
    out_dir = AGREEMENTS / county["slug"] / family
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{doc_id}.md"
    out.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                                            width=88) + "---\n" + body,
                   encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", metavar="COUNTY")
    ap.add_argument("--limit", type=int, help="first N sources per county (smoke)")
    ap.add_argument("--refetch", action="store_true")
    args = ap.parse_args()

    employers = {e["slug"]: e for e in
                 yaml.safe_load(EMPLOYERS.read_text(encoding="utf-8"))["employers"]}
    today = _dt.date.today().isoformat()
    total_ok = total_fail = 0
    skipped: list[str] = []

    for group_file in sorted(SOURCES_DIR.glob("*.yml")):
        if group_file.stem == "state":
            continue
        if args.only and group_file.stem != args.only:
            continue
        group = yaml.safe_load(group_file.read_text(encoding="utf-8"))
        county = employers[group["employer"]]
        sources = group["sources"][:args.limit] if args.limit else group["sources"]
        # CBAs first so LOAs can `related`-link to them.
        sources = sorted(sources, key=lambda s: s["family"] != "cba")
        cba_by_union: dict[str, list] = {}
        ok = 0
        for rec in sources:
            doc_id = county["slug"] + rec["id"][len(group["group"]):]
            pdf = SNAPSHOTS / f"{doc_id}.pdf"
            txt = SNAPSHOTS / f"{doc_id}.txt"
            try:
                fetched_url = rec["url"]
                src_fmt = "pdf"
                if rec["format"] == "html":
                    resolved, page = html_source(rec["url"], args.refetch)
                    if resolved:
                        fetched_url = resolved
                        fetch(fetched_url, pdf, args.refetch)
                        text, pages = extract(pdf, txt)
                    else:
                        text = html_main_text(page)
                        if len(text.strip()) < 200:
                            skipped.append(f"{doc_id}: HTML page has neither a document "
                                           f"link nor extractable body text — TODO: "
                                           f"human verification required")
                            continue
                        src_fmt = "html"
                        (SNAPSHOTS / f"{doc_id}.html").write_text(page, encoding="utf-8")
                        txt.write_text(text, encoding="utf-8")
                        pages = 0
                else:
                    fetch(fetched_url, pdf, args.refetch)
                    text, pages = extract(pdf, txt)
                if len(text.strip()) < 200:
                    skipped.append(f"{doc_id}: extraction under 200 chars (image-only "
                                   f"scan?) — TODO: OCR pass required, not ingested")
                    txt.unlink(missing_ok=True)
                    continue
                sha = hash_snapshot(doc_id, src_fmt, SNAPSHOTS)
                out = write_doc(county, rec, doc_id, sha, pages, text, today,
                                cba_by_union, fetched_url, src_fmt)
                if rec["family"] == "cba":
                    u = union_of(rec["title"])
                    if u:
                        cba_by_union.setdefault(u, []).append(doc_id)
                ok += 1
            except Exception as e:                               # noqa: BLE001
                print(f"FAIL {doc_id}: {e}", file=sys.stderr)
                total_fail += 1
        total_ok += ok
        print(f"{group['group']:12} ingested {ok}/{len(sources)}")

    print(f"\ntotal ingested {total_ok}, failed {total_fail}, skipped {len(skipped)}")
    for s in skipped:
        print(f"  skipped: {s}")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
