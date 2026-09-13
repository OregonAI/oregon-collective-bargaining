#!/usr/bin/env python3
"""Ingest county-tier agreements from the approved source groups: fetch, snapshot,
hash, write summary-mode documents under agreements/<employer>/{cba,loa}/.

  python3 src/ingest_counties.py                 # every county group
  python3 src/ingest_counties.py --only multnomah
  python3 src/ingest_counties.py --limit 3       # first N sources per county (smoke)
  python3 src/ingest_counties.py --refetch
  python3 src/ingest_counties.py --check         # report what a run would do; write nothing

NETWORK ACCESS IS OPT-IN FOR ALREADY-INGESTED SOURCES (#93). A source already
ingested, with its committed extraction (`<id>.txt`) present and its manifest
record still matching what is committed, is reused as-is unless `--refetch` is
given: no fetch, no re-extraction, no rewrite. A source whose manifest record has
changed (a re-posted URL, a re-surveyed title) is resynced from the CACHED
extraction instead -- also no network, but the document IS rewritten (finding 2).

THIS IS NOT A CLAIM THAT A NO-FLAG RUN TOUCHES NO NETWORK AT ALL. Any source with
NO committed extraction yet -- never ingested, or a metadata-only OCR stub whose
text was deliberately withheld -- still fetches, `--refetch` or not: there is
nothing cached to reuse or resync from. Measured against this corpus's real,
committed manifest (`--check`, 2026-09-12; code review finding 5, fix/safe-reingest):
134 sources reuse (manifest matches, no network), 29 are new (all Deschutes, which
republished its library at new DocumentCenter ids -- see the CHANGELOG for the
`supersedes` gap this leaves, tracked separately), and 2 are metadata-only stubs
with no committed snapshot. So a plain no-flag run today makes 31 network fetches
and writes 29 new documents -- pre-existing on main, not introduced by this
branch's fixes, but it means "safe to run" only holds for sources already fully
ingested. `--check` reports, per source, which of "ingest new / reuse (manifest
matches) / resync (manifest changed, no network) / go to the network (no cached
extraction)" a real run would do, without doing any of them.

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

OCR POLICY (--ocr): the platform's TWO-ENGINE standard, per the kpm reference
implementation (src/ocr_corroborate.py here is the same contract). tesseract
(ocrmypdf) is the primary; PaddleOCR reads the ORIGINAL scan as the cross-check;
a document ingests only if word-sequence agreement >= 0.80 AND the dictionary
gate passes (vocabulary built from this corpus's own non-OCR snapshots — never
from OCR output). Failures are skipped with their scores printed: human review,
not rejection, but never silent ingestion. Two rules on top:
  * `references_external` is WITHHELD on OCR documents regardless of score —
    kpm measured figure agreement 3-9 points below word agreement, and here a
    misread digit resolves a citation to the WRONG STATUTE while looking cited.
  * frontmatter carries `text_source: ocr` (the kpm marker), which is also what
    keeps these extractions OUT of the vocabulary that judges future OCR.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from corpus_toolkit import config as config_mod         # noqa: E402
from corpus_toolkit.documents import write_document     # noqa: E402
from corpus_toolkit.repo import hash_snapshot, parse_frontmatter  # noqa: E402
from corpus_toolkit.sources.fetch import Fetcher, sniff  # noqa: E402
from corpus_toolkit.sources.snapshots import retrieved_date  # noqa: E402

import ocr_corroborate as occ                           # noqa: E402

SOURCES_DIR = REPO_ROOT / "_meta" / "sources"
EMPLOYERS = REPO_ROOT / "_meta" / "employers.yml"
SNAPSHOTS = REPO_ROOT / "_meta" / "snapshots"
CONFIG = config_mod.load(REPO_ROOT / "_meta" / "corpus.yml")
FETCHER = Fetcher(CONFIG)
AGREEMENTS = REPO_ROOT / "agreements"

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



def fetch(url: str, dest: Path | None, refetch: bool,
         expect_pdf: bool = True) -> tuple[bytes, bool]:
    """Fetch (to `dest` when given, cached unless `refetch`) through the toolkit Fetcher:
    honest agent, HTTP/2, per-host interval, 429 backoff, refusals raised (ADR-0016).
    Returns (bytes, fresh) -- `fresh` is False exactly when `dest` was already cached
    on disk and no request was made (`FETCHER.snapshot`'s own contract). `dest=None`
    (the HTML index-page fetch) has no cache to hit, so it is always `fresh=True`.
    Callers MUST use `fresh` to decide whether `retrieved` may advance (finding 4,
    fix/safe-reingest: this return value used to be discarded (`data, _ = ...`), so
    `retrieved` stamped today's date even on a cached, zero-network read)."""
    if dest is not None:
        data, fresh = FETCHER.snapshot(url, dest, refetch)
    else:
        data, fresh = FETCHER.get(url).body, True
    if expect_pdf and sniff(data, "pdf") != "pdf":
        if dest is not None:
            dest.unlink(missing_ok=True)
        raise ValueError(f"response is not a PDF ({data[:40]!r})")
    return data, fresh


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
    """(document_url, page_html) for an HTML source: a linked document wins (Clackamas's
    dochub uuids, Benton's wp-content uploads); otherwise the page itself is the
    document (Clackamas publishes several agreements' text inline)."""
    page, _ = fetch(url, None, refetch, expect_pdf=False)
    page = page.decode("utf-8", errors="replace")
    links = DOCHUB.findall(page) or re.findall(r'href="(https?://[^"]+\.pdf)"', page)
    return (links[0] if links else None), page


def html_main_text(page: str) -> str:
    """The page's main-content text — the agreement text Clackamas publishes inline."""
    m = re.search(r"<main.*?</main>", page, re.S)
    body = m.group(0) if m else page
    body = re.sub(r"<(script|style|nav|header|footer).*?</\1>", " ", body, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    return "\n".join(" ".join(l.split()) for l in re.split(r"\s{2,}|\n", text) if l.strip())


# Fields the source cannot supply on every run: `union` and `term` come from the
# county index and the document's own text (own_dates), not the ingester's own logic;
# `effective_date`/`expiry_date` likewise; `agency_registry_slugs` is a human curation
# pass this ingester never performs (it always starts a document at `[]`); and
# `reproduction_basis` is this ingester's own computed constant but is listed here
# too per the issue that named it (oregon-collective-bargaining#93) as defence in
# depth. A re-ingest that cannot freshly reproduce one of these must carry the
# committed value forward, never silently overwrite it with empty -- the same
# whole-row-survival shape as executive-regulatory-frameworks#353's preserve_manual().
NON_DERIVABLE_FIELDS = ("union", "term", "effective_date", "expiry_date",
                        "agency_registry_slugs", "reproduction_basis")

# A stub commits no text (write_doc's own comment at the `stub` branch: "nothing
# text-derived is trusted: term only as the county's index stated it, no dates, no
# citations"). `term`, `effective_date` and `expiry_date` in NON_DERIVABLE_FIELDS are
# either text-derived (`own_dates()`) or, for `term`, sourced from the index at ingest
# time -- carrying any of the three forward from a PRIOR (non-stub) extraction would
# re-assert them as read from text this document declares it does not hold (code
# review finding 1, fix/safe-reingest: reproduced against a real Benton document
# whose source was later replaced by an image-only scan -- the exact Lane/Marion
# in-place-overwrite scenario AGENTS.md names). `union`, `agency_registry_slugs` and
# `reproduction_basis` are index/curation/computed fields, not text-derived, and are
# safe to carry forward on this path.
STUB_SAFE_FIELDS = ("union", "agency_registry_slugs", "reproduction_basis")


def load_existing(path: Path) -> dict | None:
    """The currently committed frontmatter at `path`, or None when this document has
    never been ingested before. A file that exists but fails to parse is NOT the same
    as "never ingested" -- it is reported as a failure (the caller's exception handler
    does that), never silently treated as absent. Treating "could not check" as "is
    not there" is exactly the failure this corpus's rules forbid: it would make a
    real, unreadable document look like a blank slate to overwrite."""
    if not path.is_file():
        return None
    fm, _ = parse_frontmatter(path)
    return fm


def carry_forward_nonderivable(fresh: dict, existing: dict | None,
                               fields: tuple[str, ...] = NON_DERIVABLE_FIELDS) -> dict:
    """Mutate and return `fresh`: for each of `fields` (default NON_DERIVABLE_FIELDS),
    a value this run could not (re)produce -- empty string, empty list, None -- is
    replaced by the committed document's value for that field. A value this run DID
    produce (a term the document's own text stated; a future curation pass populating
    agency_registry_slugs) wins over the committed value, because that is this run's
    own fresh finding, not a gap. `existing=None` (no prior document) is a no-op --
    there is nothing to carry forward for a document ingested for the first time.

    Callers on the stub path MUST pass `fields=STUB_SAFE_FIELDS` -- see the comment
    there for why (finding 1, fix/safe-reingest)."""
    if not existing:
        return fresh
    for field in fields:
        if not fresh.get(field) and existing.get(field):
            fresh[field] = existing[field]
    return fresh


def _carried_page_count(existing: dict | None) -> int:
    """Best-effort page count for a no-network manifest resync (finding 2): `pdfinfo`
    needs the raw PDF, which is not guaranteed cached locally, and re-deriving it is
    not the point of a resync that only propagates `source_url`/`title`. Reuses the
    count already published in the committed document's own `conversion_notes`
    rather than fabricating a fresh read; 0 when none is found (e.g. an HTML source,
    which never states a page count)."""
    text = (existing or {}).get("conversion_notes", "")
    m = re.search(r"(\d+)\s+pages", text)
    return int(m.group(1)) if m else 0


def manifest_drift(existing: dict | None, rec: dict, county: dict) -> list[str]:
    """Manifest fields that differ from what is committed, checked with NO network --
    the fresh source manifest (`_meta/sources/<county>.yml`, regenerated by
    `src/discover_counties.py` -- it DOES move, e.g. the 2026-08-25 re-survey) is
    compared against the committed document's frontmatter. Empty when there is
    nothing to compare (never ingested) or when every field this ingester's OWN
    manifest carries still agrees.

    Finding 2 (code review, fix/safe-reingest): the old reuse short-circuit
    (`out.is_file() and txt.is_file()`) never performed this compare at all, so a
    source re-posted at a new URL, or whose index title/term changed, kept its
    stale committed value forever -- no flag short of `--refetch` (a real network
    fetch for the whole county) propagated it, though propagating a manifest
    change needs no network. Only `source_url` and the title baked into `title` are
    checked here -- they are the two fields this ingester's manifest actually
    carries into the document. `union`/`term`/dates are text- or index-derived, not
    manifest fields, and a full content compare is corpus-detect-changes's job, run
    separately and monthly (see AGENTS.md's "Explicitly NOT a finding") -- this is
    NOT a hash compare and DRIFT.md's "unchanged" is not claimed for it.

    `source_url` is checked ONLY for a `pdf`-format source. An HTML-format source
    whose page links a document (Clackamas's dochub pattern, Benton's wp-content
    pattern -- both documented in this ingester's own top-of-file docstring)
    legitimately commits a DIFFERENT `source_url` than `rec['url']`: the manifest's
    `url` is the intermediate index page, while the committed `source_url` is
    whichever URL was actually fetched -- resolving that requires the network fetch
    this compare must not make. Comparing them directly false-positives on every
    such source: found by running this check against the real corpus while
    verifying finding 2's fix, not invented -- 4 real Clackamas documents commit
    their resolved dochub link as `source_url` while the manifest (correctly)
    still carries the intermediate page as `url`."""
    if not existing:
        return []
    drifted = []
    if rec.get("format") != "html" and existing.get("source_url") != rec["url"]:
        drifted.append("source_url")
    expected_title = f"{county['name']} — {rec['title']}"
    if existing.get("title") != expected_title:
        drifted.append("title")
    return drifted


def classify(out: Path, txt: Path, refetch: bool, *, rec: dict | None = None,
            county: dict | None = None) -> str:
    """What a real run would do for this source, without touching the network or
    writing anything -- the `--check` seam. Shapes:
      * never ingested before -> a real run would fetch and ingest it.
      * --refetch given -> a real run goes to the network regardless.
      * ingested, with no committed snapshot to reuse (e.g. a metadata-only OCR
        stub) -> a real run goes to the network -- there is nothing here to reuse.
      * ingested, with a committed snapshot (.txt), and the fresh manifest (`rec`/
        `county`, when given) still agrees with what is committed -> reused, no
        network. NEVER reported as "unchanged" (finding 3): this only checked the
        manifest fields the ingester itself carries, not the source bytes -- a real
        content compare is corpus-detect-changes's job, not this ingester's.
      * ingested, with a committed snapshot, but the fresh manifest DISAGREES with
        what is committed -> a real run would resync from the cached snapshot with
        no network, UNLESS the committed document is OCR'd or a metadata-only stub
        (whose provenance cannot be honestly reconstructed without re-running OCR)
        or the raw snapshot is not cached locally -- either of those needs
        `--refetch` instead, and is reported as such rather than silently reused or
        fabricated (AGENTS.md's overriding rule cuts both ways).
    """
    if not out.is_file():
        return "new — would fetch and ingest"
    if refetch:
        return "--refetch requested — would re-verify against the source"
    if not txt.is_file():
        return "no committed snapshot to reuse (e.g. a metadata-only stub) — would fetch"
    if rec is None or county is None:
        return "reused — no network (manifest not compared)"
    existing = load_existing(out)
    drifted = manifest_drift(existing, rec, county)
    if not drifted:
        return "reused — manifest matches, no network"
    if existing and (existing.get("text_source") == "ocr"
                     or existing.get("content_mode") == "summary"):
        return (f"manifest changed ({', '.join(drifted)}) but the committed document "
                f"is OCR'd/a stub — needs --refetch to resync safely, not "
                f"auto-resynced")
    return f"manifest changed ({', '.join(drifted)}) — would resync from cached snapshot, no network"


def write_doc(county: dict, rec: dict, doc_id: str, sha: str, pages: int, text: str,
              today: str, cba_by_union: dict, fetched_url: str,
              src_fmt: str = "pdf", ocr: dict | None = None,
              stub: dict | None = None, *, fresh: bool = True,
              snapshot_hint: Path | None = None) -> Path:
    family = rec["family"]
    title = rec["title"]
    out = AGREEMENTS / county["slug"] / family / f"{doc_id}.md"
    existing = load_existing(out)
    union = union_of(title)
    # A stub commits no text, so nothing text-derived is trusted: term only as the
    # county's index stated it, no dates, no citations.
    term, eff, exp = ((rec.get("term"), None, None) if stub
                      else own_dates(text, rec.get("term")))
    # OCR text never feeds citations: a misread digit resolves to the wrong statute
    # while looking cited (see the OCR policy note at the top of this file).
    refs = [] if ocr else sorted({f"ORS {n}" for n in ORS.findall(text)} |
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
        # `retrieved` may advance to today only when THIS run actually fetched bytes
        # (`fresh`) -- otherwise the committed document's own `retrieved` carries
        # forward (or the snapshot's mtime, for a document with no prior `retrieved`
        # to carry). Finding 4 (fix/safe-reingest): the 5 committed metadata-only
        # stubs have no `.txt`, so main()'s ordinary reuse short-circuit never
        # applies to them -- a re-run with the `.pdf` already cached locally used to
        # stamp `retrieved: today` having made zero requests. `fresh` defaults True
        # so a call site that does not know better (e.g. a genuinely new ingest)
        # keeps the old, correct behaviour.
        "retrieved": retrieved_date(fresh, doc_path=out, snapshot_path=snapshot_hint,
                                    today=today),
        "source_sha256": sha,
        "snapshot_policy": "hash-only",
        "status": "current",
        # CONTENT MODE FOLLOWS THE EXTRACTION, NOT THE CLASS.
        #
        # corpus.yml declares collective_bargaining_agreement `verbatim: true` (commit
        # 7fd9798, "Flip agreements to verbatim: mirror the full executed text"), and
        # corpus_toolkit.validate.provenance enforces it: a doc_type declared verbatim
        # must be `verbatim` or `mixed`, and `summary` is refused unless the document
        # carries a `content_exception`. This field was left hardcoded "summary" by that
        # flip, so every document this ingester wrote failed schema validation and #5's
        # OCR pass could not land -- for a reason that had nothing to do with OCR.
        #
        # A CLEAN EXTRACTION IS VERBATIM. That is the class determination and it matches
        # the 156 committed CBAs.
        #
        # AN OCR READING IS NOT (#5, operator decision 2026-09-12). A machine reading is
        # not the executed text, and this corpus is no longer summary-first, so publishing
        # one as `verbatim` would present a guessed wage rate as the agreement. The
        # template's own measurement is the reason: word agreement runs 88-98% while
        # agreement on FIGURES runs 69-85% -- and in a collective-bargaining agreement the
        # figures are the wage tables, step schedules and premium rates, which is exactly
        # what a reader acts on. So an OCR'd scan ingests as metadata plus a committed
        # snapshot, with a content_exception saying so, and no published verbatim text.
        # The document becomes findable; nobody is served a guess as the contract.
        "content_mode": "summary" if (ocr or stub) else "verbatim",
        **({"text_source": "ocr"} if ocr else {}),
        **({"content_exception": "image-only scan whose machine readings failed "
            "three-engine corroboration; no extraction committed, so the raw-byte "
            "hash cannot be re-verified from a committed .txt"} if stub else {}),
        **({"content_exception":
            "image-only scan read by OCR, not extracted. The machine reading passed "
            "three-engine corroboration and is committed as the snapshot, but it is NOT "
            "published as verbatim text: engine agreement on FIGURES runs well below "
            "agreement on words, and this document's figures are wage rates, step "
            "schedules and premium pay. Metadata and hash are trustworthy; the executed "
            "text is at source_url"} if ocr and not stub else {}),
        "reproduction_basis": (
            ("jointly-authored contract; the executed agreement is a public record of a "
             "public body (ORS 192.311-192.478) and is mirrored in full per the class "
             "determination in corpus.yml schema.doc_types (verbatim: true)")
            if not (ocr or stub) else
            ("jointly-authored contract, class verbatim: true in corpus.yml — but this "
             "source is an image-only scan, so no verbatim extraction exists to mirror; "
             "metadata plus official link, per the content_exception above")),
        "conversion_notes": (
            f"image-only scan; text WITHHELD — three OCR engines (tesseract, "
            f"paddleocr, docTR) disagree ({stub['agreement']:.0%} best word-sequence "
            f"agreement, {stub['figure_agreement']:.0%} on figures), so no machine "
            f"reading earned the snapshot; source_sha256 hashes the raw PDF bytes; "
            f"awaiting human transcription (issue #5)" if stub else
            occ.notes(ocr, ocr.get("engines", occ.ENGINES))
            + ("; the source PDF carries a digital signature — OCR ran "
                              "on a derived copy, the committed original preserves it"
                              if ocr.get("signed") else "") if ocr else
            f"pdftotext -layout; {pages} pages, "
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
    # MERGE OVER THE EXISTING DOCUMENT, don't construct a fresh one (#93): union,
    # term, effective_date, expiry_date, agency_registry_slugs and reproduction_basis
    # come from the county index, the document's own text, or a curation pass this
    # ingester never performs -- not from anything guaranteed reproducible on every
    # run. Refresh the locals `glance` (below) reads from the merged result, so the
    # curator-facing prose matches what was actually written, including anything
    # just carried forward from the committed document.
    fm = carry_forward_nonderivable(
        fm, existing, STUB_SAFE_FIELDS if stub else NON_DERIVABLE_FIELDS)
    union = fm["union"]
    term = fm["term"] or None
    eff = fm["effective_date"] or None
    exp = fm["expiry_date"] or None
    # `citation` was built from the PRE-merge term/union; recompute it so a term
    # carried forward by the merge above still shows up in the citation string.
    cite_bits = [term, county["name"], union or title, "agreement" if family == "cba"
                 else "letter of agreement"]
    fm["citation"] = " ".join(b for b in cite_bits if b)

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
    if stub:
        glance.insert(0, "**METADATA-ONLY RECORD — no text is held.** This is an "
                         "image-only scan whose machine readings failed three-engine "
                         "corroboration (see conversion_notes). Everything on this page "
                         "comes from the county's index listing; read the document "
                         "itself at the official source link.")
    if ocr:
        glance.append(f"- **The source is an image-only scan.** Its committed text is a "
                      f"machine reading corroborated by two independent OCR engines "
                      f"({ocr['agreement']:.0%} word-sequence agreement — see "
                      f"conversion_notes). Dates and terms above come from that reading; "
                      f"statute citations are deliberately not extracted, because digits "
                      f"are where engines diverge.")
    if fetched_url != rec["url"]:
        glance.append(f"- Fetched via the county's document CDN: {fetched_url} "
                      f"(the index links an intermediate page; see Curator notes)")

    src_note = rec.get("notes")
    body = f"""
> **NON-AUTHORITATIVE — AI-friendly reference only.** This is a curated
> summary, not the agreement's official text. Verify against the official
> source: <{rec['url']}> (retrieved {today}).

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
    out.parent.mkdir(parents=True, exist_ok=True)
    # Frontmatter order, defaults and schema validation are the toolkit's; a document that
    # would fail CI is refused here with every finding named (ADR-0016).
    return write_document(CONFIG, out, fm, body)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", metavar="COUNTY")
    ap.add_argument("--limit", type=int, help="first N sources per county (smoke)")
    ap.add_argument("--stubs", action="store_true",
                    help="ingest scans that fail the OCR gate as METADATA-ONLY stubs "
                         "(content_exception; no text committed) — issue #5's terminal "
                         "state for all-engine disagreements, upgradeable by human "
                         "transcription later")
    ap.add_argument("--ocr", action="store_true",
                    help="recover image-only scans with ocrmypdf (tesseract) — see the "
                         "OCR policy note in this docstring")
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="report what a real run would do for each source -- ingest, "
                         "reuse the committed snapshot, or go to the network -- and exit "
                         "without fetching, extracting or writing anything (#93)")
    args = ap.parse_args()

    employers = {e["slug"]: e for e in
                 yaml.safe_load(EMPLOYERS.read_text(encoding="utf-8"))["employers"]}
    today = _dt.date.today().isoformat()
    # Kept apart, never summed into one "ingested" figure (AGENTS.md #4/finding 3):
    # a freshly-fetched document, a no-network manifest resync, and a plain reuse
    # are three different claims about how much was actually checked.
    total_new = total_resynced = total_reused = total_fail = total_examined = 0
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
        new = resynced = reused = fail = 0
        for rec in sources:
            doc_id = county["slug"] + rec["id"][len(group["group"]):]
            pdf = SNAPSHOTS / f"{doc_id}.pdf"
            txt = SNAPSHOTS / f"{doc_id}.txt"
            out = AGREEMENTS / county["slug"] / rec["family"] / f"{doc_id}.md"
            if args.check:
                print(f"  {doc_id}: {classify(out, txt, args.refetch, rec=rec, county=county)}")
                total_examined += 1
                continue
            # NETWORK ACCESS IS OPT-IN (#93): a document already ingested, with its
            # committed extraction (.txt) on disk, is reused as-is when --refetch was
            # not passed -- no fetch, no re-extraction, no rewrite, UNLESS the fresh
            # source manifest has itself changed (finding 2: a source re-posted at a
            # new URL, or whose index title changed, used to keep its stale committed
            # value forever -- no flag short of --refetch propagated it, though
            # propagating a manifest change needs no network at all). A document with
            # no committed snapshot to reuse (never ingested, or a metadata-only OCR
            # stub whose text was deliberately withheld) still falls through to the
            # fetch path below -- there is nothing here to reuse.
            if not args.refetch and out.is_file() and txt.is_file():
                existing = load_existing(out)
                drifted = manifest_drift(existing, rec, county)
                if not drifted:
                    if rec["family"] == "cba":
                        u = union_of(rec["title"])
                        if u:
                            cba_by_union.setdefault(u, []).append(doc_id)
                    reused += 1
                    total_reused += 1
                    continue
                if existing and (existing.get("text_source") == "ocr"
                                or existing.get("content_mode") == "summary"):
                    # An OCR reading's corroboration scores, or a stub's, cannot be
                    # honestly reconstructed from the manifest alone -- resyncing
                    # here without re-running OCR would assert scores this run never
                    # measured (the same fabrication finding 1 forbids on the stub
                    # path). --refetch (with --ocr/--stubs) re-derives it properly.
                    skipped.append(
                        f"{doc_id}: manifest changed ({', '.join(drifted)}) but the "
                        f"committed document is OCR'd/a stub — re-run with --refetch "
                        f"to resync safely, not auto-resynced")
                    continue
                src_fmt = existing.get("source_format", "pdf") if existing else "pdf"
                raw = SNAPSHOTS / f"{doc_id}.{src_fmt}"
                if not raw.is_file():
                    # #93's own measurement: raw snapshots are cached locally in a
                    # normal checkout (283) but mostly absent in a fresh worktree
                    # (10) -- "could not check" is never reported as "is not there"
                    # (AGENTS.md's overriding rule), so this is reported as needing
                    # --refetch, never silently skipped as if nothing had changed.
                    skipped.append(
                        f"{doc_id}: manifest changed ({', '.join(drifted)}) but the "
                        f"raw snapshot is not cached locally to resync from — "
                        f"re-run with --refetch")
                    continue
                text = txt.read_text(encoding="utf-8", errors="replace")
                sha = hash_snapshot(doc_id, src_fmt, SNAPSHOTS)
                write_doc(county, rec, doc_id, sha, _carried_page_count(existing),
                         text, today, cba_by_union, rec["url"], src_fmt, fresh=False)
                print(f"resynced {doc_id}  (manifest changed: {', '.join(drifted)}, "
                      f"no network)")
                if rec["family"] == "cba":
                    u = union_of(rec["title"])
                    if u:
                        cba_by_union.setdefault(u, []).append(doc_id)
                resynced += 1
                total_resynced += 1
                continue
            try:
                fetched_url = rec["url"]
                src_fmt = "pdf"
                # `fresh` tracks whether the DOCUMENT's own bytes were actually
                # fetched this run (as opposed to read back from a locally cached
                # snapshot) -- it is what `retrieved` may honestly advance on
                # (finding 4). The HTML index-page request inside `html_source()`
                # is always a real network call, but it is not the document when a
                # linked PDF resolves out of it -- that PDF's own fetch below is
                # what decides `fresh` in that case.
                fresh = True
                if rec["format"] == "html":
                    resolved, page = html_source(rec["url"], args.refetch)
                    if resolved:
                        fetched_url = resolved
                        _, fresh = fetch(fetched_url, pdf, args.refetch)
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
                    _, fresh = fetch(fetched_url, pdf, args.refetch)
                    text, pages = extract(pdf, txt)
                ocr = None
                if len(text.strip()) < 200 and src_fmt == "pdf":
                    if not args.ocr:
                        skipped.append(f"{doc_id}: extraction under 200 chars (image-only "
                                       f"scan?) — TODO: OCR pass required, not ingested")
                        txt.unlink(missing_ok=True)
                        continue
                    ocr_pdf = SNAPSHOTS / f"{doc_id}.ocr.pdf"
                    signed = False
                    if not ocr_pdf.is_file() or args.refetch:
                        cmd = ["ocrmypdf", "-l", "eng", "--optimize", "0",
                               "--output-type", "pdf", "--rotate-pages",
                               "--deskew", "--skip-text", str(pdf), str(ocr_pdf)]
                        r = subprocess.run(cmd, capture_output=True, text=True)
                        if r.returncode and "DigitalSignatureError" in r.stderr:
                            # The source is DIGITALLY SIGNED — a provenance fact worth
                            # keeping. OCR runs on a derived copy; the committed original
                            # snapshot preserves the signature untouched, so invalidating
                            # it on the copy alters nothing anyone verifies.
                            signed = True
                            subprocess.run(cmd[:1] + ["--invalidate-digital-signatures"]
                                           + cmd[1:], check=True, capture_output=True)
                        elif r.returncode:
                            raise RuntimeError(f"ocrmypdf failed: {r.stderr.strip()[-200:]}")
                    else:
                        signed = "digitally signed" in (
                            (SNAPSHOTS / f"{doc_id}.signed").read_text()
                            if (SNAPSHOTS / f"{doc_id}.signed").is_file() else "")
                    if signed:
                        (SNAPSHOTS / f"{doc_id}.signed").write_text("digitally signed")
                    text, pages = extract(ocr_pdf, txt)
                    if len(text.strip()) < 200:
                        # Tesseract cannot read this scan at all. The DIFFERENT-PAIR
                        # fallback (the policy repo's eo recovery pattern): docTR
                        # becomes the committed text, corroborated by paddle — two
                        # engines sharing no weights, neither of them tesseract.
                        dt = occ.doctr_text(pdf)
                        if dt and len(dt.strip()) >= 200:
                            cross2 = occ.paddle_text(pdf, SNAPSHOTS / ".paddle-work")
                            s2 = occ.score(dt, cross2, occ.vocabulary()) if cross2 else None
                            if s2 and s2["gate_ok"] and s2["agree_ok"]:
                                txt.write_text(dt, encoding="utf-8")
                                text = dt
                                s2["engines"] = ("docTR (DBNet + CRNN)",
                                                 "paddleocr PP-OCRv6")
                                s2["extra_note"] = ("different-pair recovery: tesseract "
                                                    "produced no usable text on this scan")
                                sha = hash_snapshot(doc_id, src_fmt, SNAPSHOTS)
                                out = write_doc(county, rec, doc_id, sha, pages, text,
                                                today, cba_by_union, fetched_url,
                                                src_fmt, s2, fresh=fresh,
                                                snapshot_hint=pdf)
                                if rec["family"] == "cba":
                                    u = union_of(rec["title"])
                                    if u:
                                        cba_by_union.setdefault(u, []).append(doc_id)
                                new += 1
                                total_new += 1
                                continue
                        skipped.append(f"{doc_id}: no engine pair could corroborate this "
                                       f"scan (tesseract under 200 chars; docTR/paddle "
                                       f"did not both clear the gate) — TODO: human "
                                       f"verification required")
                        txt.unlink(missing_ok=True)
                        continue
                    cross = occ.paddle_text(pdf, SNAPSHOTS / ".paddle-work")
                    if cross is None:
                        skipped.append(f"{doc_id}: PaddleOCR cross-check unavailable — "
                                       f"two-engine rule unmet, not ingested")
                        txt.unlink(missing_ok=True)
                        continue
                    s = occ.score(text, cross, occ.vocabulary())
                    s["engines"] = occ.ENGINES
                    if s["gate_ok"] and not s["agree_ok"]:
                        # TIEBREAK, per the platform stack: docTR votes. Accept only
                        # when docTR sides with TESSERACT (>= 0.80) — the committed
                        # text is tesseract's, and a paddle+docTR majority against it
                        # would corroborate text we are not committing.
                        dt = occ.doctr_text(pdf)
                        if dt:
                            s3 = occ.score(text, dt, occ.vocabulary())
                            if s3["gate_ok"] and s3["agree_ok"]:
                                s3["engines"] = ("tesseract (ocrmypdf)",
                                                 "docTR (DBNet + CRNN)")
                                s3["extra_note"] = (
                                    f"docTR tiebreak: paddleocr agreed on only "
                                    f"{s['agreement']:.0%} of the word sequence and was "
                                    f"outvoted by the tesseract+docTR pair")
                                s = s3
                    if not (s["gate_ok"] and s["agree_ok"]):
                        if args.stubs:
                            # METADATA-ONLY STUB (the ERF image-only-EO arrangement):
                            # the document exists, its index facts and official link
                            # serve, and NO machine reading is committed — three
                            # engines disagreeing means none of their texts earns the
                            # hash. Raw-byte hash of the PDF; content_exception says
                            # why CI cannot re-verify it; a human transcription
                            # upgrades this in place later.
                            txt.unlink(missing_ok=True)
                            sha = hash_snapshot(doc_id, src_fmt, SNAPSHOTS)
                            out = write_doc(county, rec, doc_id, sha, pages, "",
                                            today, cba_by_union, fetched_url,
                                            src_fmt, None, stub=s, fresh=fresh,
                                            snapshot_hint=pdf)
                            print(f"stub {out.relative_to(REPO_ROOT)}  (agreement "
                                  f"{s['agreement']:.0%} — text withheld)")
                            new += 1
                            total_new += 1
                            continue
                        skipped.append(
                            f"{doc_id}: failed the two-engine gate incl. docTR tiebreak "
                            f"(agreement {s['agreement']:.0%}, figures "
                            f"{s['figure_agreement']:.0%}, dict {s['dict_ratio']:.0%}, "
                            f"{s['words']} words) — human review required, not ingested")
                        txt.unlink(missing_ok=True)
                        continue
                    if signed:
                        s["signed"] = True
                    ocr = s
                sha = hash_snapshot(doc_id, src_fmt, SNAPSHOTS)
                out = write_doc(county, rec, doc_id, sha, pages, text, today,
                                cba_by_union, fetched_url, src_fmt, ocr, fresh=fresh,
                                snapshot_hint=pdf)
                if rec["family"] == "cba":
                    u = union_of(rec["title"])
                    if u:
                        cba_by_union.setdefault(u, []).append(doc_id)
                new += 1
                total_new += 1
            except Exception as e:                               # noqa: BLE001
                print(f"FAIL {doc_id}: {e}", file=sys.stderr)
                fail += 1
                total_fail += 1
        if args.check:
            print(f"{group['group']:12} examined {len(sources)} source(s) — "
                  f"see classifications above")
        else:
            print(f"{group['group']:12} {new} new, {resynced} resynced (manifest "
                  f"change, no network), {reused} reused (no network), {fail} failed")

    if args.check:
        print(f"\n--check examined {total_examined} source(s); nothing written")
    else:
        total_written = total_new + total_resynced
        print(f"\ntotal: {total_new} new + {total_resynced} resynced from manifest "
              f"changes = {total_written} written; {total_reused} reused (manifest "
              f"matches, no network — not a content compare, see corpus-detect-changes "
              f"for that); {total_fail} failed; {len(skipped)} skipped")
    for s in skipped:
        print(f"  skipped: {s}")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
