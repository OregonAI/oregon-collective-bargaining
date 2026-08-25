#!/usr/bin/env python3
"""Generate _meta/sources/<county>.yml for the survey-verified county publishers.

  python3 src/discover_counties.py            # rewrite all county group files
  python3 src/discover_counties.py --check    # exit 1 if any would change (CI)
  python3 src/discover_counties.py --only multnomah

WHAT THIS PARSES, AND WHY IT IS NOT A LIVE CRAWLER (yet). Each county's index page
was fetched 2026-08-02 with the platform's honest UA during the seed survey; the raw
HTML is archived beside the survey (corpus-seeds/.cba-survey/fetches-2026-08-02/).
Discovery parses THOSE fetches, so every source row below traces to an archived
byte-for-byte page a reviewer can open. Point --archive at a newer fetch directory
(same filenames) to re-discover; per-county robots re-checks belong in that same
pass. This is the oregon-counties discover→PR→ingest shape with the fetch step
already done by the survey.

One extractor per county because no two counties publish alike — the survey measured
that, and a mode no county uses is untested code that reads as capability
(oregon-counties' lesson, inherited):

  multnomah    Drupal, absolute /file/<slug>/download links, 13 CBAs, best page
  washington   Drupal, TWO document path prefixes (/hr/documents/ AND
               /support-services/documents/), CBAs plus a real LOA/MOU trove
  clackamas    heterogeneous: direct dochub.clackamas.us uuid links AND
               /des/<slug> intermediate HTML pages (second hop at ingest);
               index shows NO terms; the AFSCME DTD unit is NAMED IN PROSE WITH
               NO LINK AT ALL — recorded as a finding, not silently dropped
  lane         CivicLive; documents on a DIFFERENT host (lanecounty.org) than the
               index (lanecountyor.gov); UNDATED filenames overwritten in place
  marion       SharePoint; relative /HR/Documents/<UNION> CBA.pdf; undated,
               overwritten in place — same hashing mandate as Lane
  jackson      relative "Document Center/..." paths WITH SPACES; the index lists 3
               of >=5 known units (AFSCME lives on mijackson.org, JCSSA surfaced
               only as an ERB case exhibit — leads, not sources, recorded below)
  deschutes    CivicPlus DocumentCenter, terms in slugs, CBAs + a large MOU set;
               county is mid-migration from deschutes.org (mirror NOT seeded)
  columbia     static /media/ paths with LITERAL UNENCODED SPACES
  coos         static hashed /files/<hash>/<name>.pdf
  yamhill      CivicPlus DocumentCenter; the ONE host here with the Cloudflare
               managed AI-crawler robots block — see its crawl block
"""
from __future__ import annotations

import argparse
import html as _html
import re
import sys
import urllib.parse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "_meta" / "sources"
DEFAULT_ARCHIVE = REPO_ROOT / "_meta" / "discovery" / "2026-08-02"
ARCHIVE_DATE = "2026-08-02"   # the date of the archived fetches; travels with --archive

TERM = re.compile(r"\b(20\d{2})\s*(?:[-–]|to)\s*(20\d{2})\b")
LOA = re.compile(r"\b(loa|mou|moa|memorandum|letter of agreement|ratification|modifications?)\b", re.I)


def _txt(s: str) -> str:
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def _term(*texts: str) -> str | None:
    for t in texts:
        # WordPress slugs separate with underscores ("2022_-_2027"); normalize first.
        if m := TERM.search(urllib.parse.unquote(t or "").replace("_", " ")):
            return f"{m.group(1)}-{m.group(2)}"
    return None


def _family(*texts: str) -> str:
    return "loa" if any(LOA.search(t or "") for t in texts) else "cba"


def _slug(group: str, text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", urllib.parse.unquote(text).lower()).strip("-")
    return f"{group}-{s}"[:100]


def _norm_url(url: str) -> str:
    """Unescape entities, then percent-encode the path's hostile characters.

    Two measured failure modes drive this: (1) hrefs arrive entity-escaped
    (&amp; in Multnomah's slugs) and stored verbatim they 404 in a way that looks
    like link rot — the oregon-audits lesson, met again; (2) markdown parsers
    (lychee in CI) read `_..._` in a slug as EMPHASIS and truncate the URL at the
    first underscore — Multnomah's `/file/_international_...(ibew)_...` scanned as
    `/file/` and 404'd CI. Underscores are unreserved, so %5F is the same resource
    to the server and inert to markdown. quote() with '%' safe keeps existing %20s
    from double-encoding; parentheses and apostrophes encode too."""
    u = _html.unescape(url)
    m = re.match(r"(https?://[^/]+)(/[^?]*)?(\?.*)?$", u)
    if not m:
        return u
    path = urllib.parse.quote(m.group(2) or "", safe="/%").replace("_", "%5F")
    return m.group(1) + path + (m.group(3) or "")


def _mk(group: str, url: str, title: str, fmt: str = "pdf", **extra) -> dict:
    rec = {"id": _slug(group, title), "url": _norm_url(url),
           "family": extra.pop("family", None) or _family(title, url),
           "format": fmt, "sha256": "", "title": title}
    if t := _term(title, url):
        rec["term"] = t
    rec["last_checked"] = ARCHIVE_DATE
    rec.update({k: v for k, v in extra.items() if v})
    return rec


# ── per-county extractors: (archive html) -> list[source dict] ──────────────────

def x_multnomah(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="(?:https://(?:www\.)?multco\.us)?(/file/[^"]+/download)"[^>]*>(.*?)</a>', t, re.S):
        out.append(_mk("multnomah", "https://multco.us" + m.group(1), _txt(m.group(2))))
    return out


def x_washington(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="((?:/hr|/support-services)/documents/[^"]+/download[^"]*)"[^>]*>(.*?)</a>', t, re.S):
        title = re.sub(r"\s*\(PDF[^)]*\)\s*$", "", _txt(m.group(2)))
        out.append(_mk("washington", "https://www.washingtoncountyor.gov" + m.group(1), title))
    return out


def x_clackamas(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="(https://dochub\.clackamas\.us/documents/drupal/[^"]+)"[^>]*>(.*?)</a>', t, re.S):
        title = _txt(m.group(2))
        if "county code" in title.lower():
            continue   # Chapter 2.05 is county LAW — oregon-counties' domain, not this corpus
        out.append(_mk("clackamas", m.group(1), title,
                       notes="dochub CDN uuid URL — no filename, stability unproven; hash on first fetch."))
    for m in re.finditer(r'href="(https://www\.clackamas\.us/des/[a-z0-9-]+)"[^>]*>(.*?)</a>', t, re.S):
        url, title = m.group(1), _txt(m.group(2))
        if url.endswith("/des/contracts") or not title:
            continue
        out.append(_mk("clackamas", url, title, fmt="html",
                       notes="Intermediate HTML page for this unit/instrument — the document is a "
                             "second hop behind it; resolve and hash the target at ingest."))
    return out


def x_lane(t: str) -> list[dict]:
    out, seen = [], set()
    for m in re.finditer(r'href="(https://www\.lanecounty\.org/[^"]+\.pdf)"', t):
        url = m.group(1)
        fname = urllib.parse.unquote(url.rsplit("/", 1)[1])[:-4]
        if fname in seen:
            continue
        seen.add(fname)
        out.append(_mk("lane", url, fname,
                       notes="UNDATED filename overwritten in place upstream — the term is only "
                             "inside the document; content hash is the only change signal."))
    return out


def x_marion(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="(/HR/Documents/[^"]+\.pdf)"', t):
        url = m.group(1)
        fname = urllib.parse.unquote(url.rsplit("/", 1)[1])[:-4]
        if "cba" not in fname.lower():
            continue   # the page mixes pay plans and benefits matrices with the CBAs
        out.append(_mk("marion", "https://www.co.marion.or.us" + url, fname,
                       notes="UNDATED filename overwritten in place upstream — same hashing "
                             "mandate as Lane."))
    return out


def x_jackson(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="([^"]*Labor Agreements/[^"]+\.pdf)(?:\?[^"]*)?"[^>]*>(.*?)</a>', t, re.S):
        url = m.group(1)   # the ?t=<stamp> cache-buster is dropped: it changes per upload
        if not url.startswith("http"):
            url = "https://jacksoncountyor.gov/" + url.lstrip("/")
        out.append(_mk("jackson", url, _txt(m.group(2)),
                       notes="Upstream href carries a ?t= cache-buster (dropped here — it moves "
                             "on every re-upload, so its CHANGE is itself an update signal worth "
                             "checking at re-discovery)."))
    return out


def x_deschutes(t: str) -> list[dict]:
    out, seen = [], set()
    for m in re.finditer(r'href="(/DocumentCenter/View/\d+/[^"]+)"[^>]*>(.*?)</a>', t, re.S):
        url = "https://www.deschutescounty.gov" + m.group(1)
        if url in seen:
            continue
        seen.add(url)
        out.append(_mk("deschutes", url, _txt(m.group(2))))
    return out


def x_columbia(t: str) -> list[dict]:
    out, seen = [], set()
    for m in re.finditer(r'href="(https://www\.columbiacountyor\.gov/media/[^"]*Union Contracts/[^"]+)"', t):
        url = m.group(1)
        fname = urllib.parse.unquote(url.rsplit("/", 1)[1])
        fname = re.sub(r"\.pdf$", "", fname, flags=re.I)
        if url in seen:
            continue
        seen.add(url)
        out.append(_mk("columbia", url, fname,
                       notes="Upstream URL contains literal unencoded spaces; percent-encoded here."))
    return out


def x_coos(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="(/files/[^"]+\.pdf)"[^>]*>(.*?)</a>', t, re.S):
        title = _txt(m.group(2)) or urllib.parse.unquote(m.group(1).rsplit("/", 1)[1])
        if "cba" not in (title + m.group(1)).lower():
            continue   # drops e.g. the public-records-request form
        out.append(_mk("coos", "https://co.coos.or.us" + m.group(1), re.sub(r"\.pdf$", "", title, flags=re.I)))
    return out


def x_benton(t: str) -> list[dict]:
    """Benton's careers-and-benefits page IS the labor index (found on the tranche-2
    hunt after the survey's not-located): three unit links in the bargaining section —
    one an intermediate WordPress page (AFSCME), two direct wp-content PDFs."""
    out = []
    for m in re.finditer(r'href="(https://hr\.bentoncountyor\.gov/[^"]+)"[^>]*>([^<]{10,120})', t):
        url, label = m.group(1), _txt(m.group(2))
        if not re.search(r"Federation of State|Sheriff|Nurses Association", label):
            continue
        if url.endswith(".pdf"):
            out.append(_mk("benton", url, label))
        else:
            out.append(_mk("benton", url, label, fmt="html",
                           notes="Intermediate WordPress page — the wp-content PDF is "
                                 "resolved out of it at ingest."))
    return out


def x_yamhill(t: str) -> list[dict]:
    out = []
    for m in re.finditer(r'href="([^"]*DocumentCenter/View/\d+/[^"]+)"[^>]*aria-label="([^"]+)"', t):
        label = _html.unescape(m.group(2)).replace(" pdf file", "").strip()
        if "CBA" not in label:
            continue   # the page also links the county budget book
        url = m.group(1)
        if not url.startswith("http"):
            url = "https://www.yamhillcounty.gov/" + url.lstrip("/")
        out.append(_mk("yamhill", url, re.sub(r"\s*\(PDF\)\s*$", "", label)))
    return out


# ── per-county publication facts: index, crawl determination, signals ───────────

def _stock_host(host: str, notes: str) -> dict:
    return {"host": host, "robots_url": f"https://{host}/robots.txt",
            "ai_block": False, "content_signal": None, "notes": notes}


COUNTIES: dict[str, dict] = {
    "multnomah": dict(
        employer="multnomah-county", extractor=x_multnomah,
        title="Multnomah County labor contracts",
        index="https://multco.us/info/labor-contracts",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="Stock Drupal robots.txt: framework paths only (/core/, /profiles/, "
                         "READMEs); nothing blocks /file/ or /info/. No AI-agent rules.",
                   hosts=[_stock_host("multco.us", "Drupal; www redirects to the bare host. "
                                      "Several file slugs contain literal parentheses, "
                                      "apostrophes and ampersands — encode before fetching.")]),
        upstream="No feed. Index table lists each unit with its term; re-fetch the index, diff "
                 "the link set, re-hash documents. The best-organized labor page in the state.",
        header=[]),
    "washington": dict(
        employer="washington-county", extractor=x_washington,
        title="Washington County labor agreements",
        index="https://www.washingtoncountyor.gov/hr/labor-agreements",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="Stock Drupal robots.txt, framework paths only; nothing blocks either "
                         "documents prefix. No AI-agent rules.",
                   hosts=[_stock_host("www.washingtoncountyor.gov",
                                      "Drupal. Documents live under TWO prefixes — /hr/documents/ "
                                      "AND /support-services/documents/ — both enumerated here; "
                                      "an ingester watching only /hr/ silently loses three units.")]),
        upstream="No feed; re-fetch index and diff links. Washington also posts the LOA/MOU layer "
                 "(certification pay, insurance, schedules) most counties never publish — the "
                 "richest loa set in the county tier.",
        header=[]),
    "clackamas": dict(
        employer="clackamas-county", extractor=x_clackamas,
        title="Clackamas County union contracts",
        index="https://www.clackamas.us/des/contracts",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="Drupal stock robots.txt on www.clackamas.us (framework + /search/ "
                         "paths); dochub.clackamas.us serves no robots.txt at all (404) — "
                         "absence of a policy recorded as measured, not assumed as consent; "
                         "it is the county's own document CDN.",
                   hosts=[_stock_host("www.clackamas.us", "Index + intermediate unit pages."),
                          {"host": "dochub.clackamas.us", "robots_url": None, "ai_block": False,
                           "content_signal": None,
                           "notes": "robots.txt 404s. County document CDN serving uuid URLs "
                                    "with no filenames; durability unproven — hash on first "
                                    "fetch and treat URL changes as expected."}]),
        upstream="No feed, and the INDEX SHOWS NO TERMS — dating requires opening each document. "
                 "Mixed link shapes (direct CDN uuid + intermediate HTML pages) enumerated here.",
        header=["FINDING: the index names the AFSCME DTD (Transportation & Development) unit in "
                "prose but links NO document for it — recorded as a gap at the publisher, "
                "not skipped silently. The CCOM 9-1-1 and WES AFSCME units DO have pages.",
                "EXCLUDED on purpose: 'Chapter 2.05 of the County Code' (county LAW — belongs "
                "to the oregon-counties corpus, not here)."]),
    "lane": dict(
        employer="lane-county", extractor=x_lane,
        title="Lane County collective bargaining agreements",
        index="https://www.lanecountyor.gov/government/county_departments/human_resources/collective_bargaining_agreements",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="Identical CivicLive robots.txt on both hosts: /Search/, /WebApi/ and "
                         "widget service paths only; nothing blocks /UserFiles/. No AI rules.",
                   hosts=[_stock_host("www.lanecountyor.gov", "Index host."),
                          _stock_host("www.lanecounty.org",
                                      "DOCUMENT host — different domain than the index; also "
                                      "mirrored via cdnsm5-hosted.civiclive.com (mirror not "
                                      "seeded; dedupe by hash if it ever is).")]),
        upstream="No feed, and the worst change signal in the tier: UNDATED, UNVERSIONED "
                 "filenames overwritten in place. Content hashing is the ONLY update detection; "
                 "a filename-diff shows nothing, forever.",
        header=[]),
    "marion": dict(
        employer="marion-county", extractor=x_marion,
        title="Marion County union contracts",
        index="https://www.co.marion.or.us/HR/Pages/payplan.aspx",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="SharePoint-era robots.txt: /_catalogs plus two named SEO bots; nothing "
                         "blocks /HR/Documents/. No AI-agent rules.",
                   hosts=[_stock_host("www.co.marion.or.us",
                                      "Index page mixes CBAs with pay plans and benefits "
                                      "matrices; only files named *CBA* are seeded. Note the "
                                      "counties corpus found Marion's CODE vendor behind "
                                      "Cloudflare — the county's own site serves fine, which is "
                                      "the same split measured there.")]),
        upstream="No feed; undated '<UNION> CBA.pdf' filenames overwritten in place — same "
                 "hashing mandate as Lane.",
        header=[]),
    "jackson": dict(
        employer="jackson-county", extractor=x_jackson,
        title="Jackson County labor agreements",
        index="https://jacksoncountyor.gov/departments/administration/human_resources/labor_agreements.php",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="jacksoncountyor.gov serves no robots.txt (404) — recorded as measured. "
                         "Static PHP site; document paths contain literal spaces.",
                   hosts=[{"host": "jacksoncountyor.gov", "robots_url": None, "ai_block": False,
                           "content_signal": None,
                           "notes": "robots.txt 404s. Paths under 'Document Center/' with "
                                    "spaces; percent-encoded here."},
                          {"host": "www.oregon.gov",
                           "robots_url": "https://www.oregon.gov/robots.txt",
                           "ai_block": False, "content_signal": None,
                           "notes": "Hosts the JCSSA ERB case-file exhibit — the same "
                                    "robots determination as the state group (no relevant "
                                    "disallow, fetched at survey time)."}]),
        upstream="No feed. THE INDEX IS A FLOOR, NOT THE COVERAGE: 3 units listed, >=5 known.",
        header=["INDEX INCOMPLETE — the two survey leads were fetched and verified "
                "2026-08-02, with opposite outcomes:",
                "  FALSE LEAD, rejected: mijackson.org is Jackson County, MICHIGAN — its "
                "DocumentCenter CBA names 'Michigan Council No. 25 AFSCME'. The search "
                "artifact conflated the two counties; Oregon Jackson County's AFSCME "
                "agreement remains publicly unlocated (records request is the path).",
                "  VERIFIED, seeded below as an extra source: the JCSSA (Sheriff's "
                "Sergeants) 2023-2026 agreement, whose only public copy is an ERB case "
                "exhibit — labeled as exactly that, per this corpus's exception rule."],
        extra=[{
            "id": "jackson-jcssa-sheriffs-sergeants-2023-2026-erb-exhibit",
            "url": "https://www.oregon.gov/erb/Documents/ME-008-26_JCSSA-FOCS.pdf",
            "family": "cba", "format": "pdf", "sha256": "",
            "title": "Jackson County Sheriff's Sergeants' Association (JCSSA) agreement "
                     "2023-2026 — ERB case exhibit copy",
            "union": "JCSSA", "term": "2023-2026", "last_checked": ARCHIVE_DATE,
            "notes": "THE ONLY PUBLIC COPY, and it is an Oregon ERB case-file exhibit "
                     "(case ME-008-26), not a county publication — the county's own index "
                     "does not list this unit. Hand-verified 2026-08-02 (fetched; cover "
                     "page names the association and the 2023-2026 term). An exhibit copy "
                     "may lag amendments; treat the county as the source of record the "
                     "day it publishes one.",
        }]),
    "deschutes": dict(
        employer="deschutes-county", extractor=x_deschutes,
        title="Deschutes County labor contracts and documents",
        index="https://www.deschutescounty.gov/1095/Labor-Contracts-and-Documents",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="CivicPlus stock robots.txt (admin/search paths, Baidu/Yandex blocks); "
                         "nothing blocks /DocumentCenter/. No AI-agent rules — note the SAME "
                         "platform serves Linn and Douglas, which 403 the honest UA: blocking "
                         "is per-site config, and this site does not.",
                   hosts=[_stock_host("www.deschutescounty.gov",
                                      "MID-MIGRATION: an older mirror lives at "
                                      "deschutes.org/hr/page/labor-contracts with different "
                                      "paths. The mirror is NOT seeded; prefer this domain, "
                                      "dedupe by hash if the old one resurfaces.")]),
        upstream="No feed; DocumentCenter slugs carry terms and DC order numbers, so an index "
                 "link-set diff is meaningful here, unlike Lane/Marion.",
        header=[]),
    "columbia": dict(
        employer="columbia-county", extractor=x_columbia,
        title="Columbia County union contracts",
        index="https://www.columbiacountyor.gov/departments/HumanResources/union-contracts",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="Minimal robots.txt: search-view query paths only. No AI-agent rules.",
                   hosts=[_stock_host("www.columbiacountyor.gov",
                                      "Static /media/ paths with LITERAL UNENCODED SPACES — "
                                      "percent-encoded in the URLs here.")]),
        upstream="No feed; re-fetch index and diff links. Terms are in the filenames.",
        header=[]),
    "coos": dict(
        employer="coos-county", extractor=x_coos,
        title="Coos County union contracts",
        index="https://co.coos.or.us/union-contracts",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="robots.txt blocks only SEO crawlers (Semrush, Ahrefs, MJ12 etc.); no "
                         "AI-agent rules; nothing blocks /files/.",
                   hosts=[_stock_host("co.coos.or.us",
                                      "Hashed-directory static files (/files/<hash>/<name>.pdf) — "
                                      "a re-upload gets a NEW hash directory, so link-set diffs "
                                      "detect updates here. The old www.co.coos.or.us index URL "
                                      "404s; not seeded. TLS CERT EXPIRED 2026-08-03 (the day "
                                      "after ingest) — documents intact behind the broken cert; "
                                      "link checks ignore the host until renewal.")]),
        upstream="Hashed file paths mean upstream updates change URLs — index link-set diff is "
                 "the change signal.",
        header=[]),
    "benton": dict(
        employer="benton-county", extractor=x_benton,
        title="Benton County labor agreements",
        index="https://hr.bentoncountyor.gov/careers-and-benefits/",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="hr.bentoncountyor.gov robots.txt is a universal allow "
                         "(User-agent: * / empty Disallow); no AI-agent rules. Note the "
                         "counties corpus measured Benton's CODE vendor blocking "
                         "ClaudeBot — the county's own HR subdomain does not.",
                   hosts=[_stock_host("hr.bentoncountyor.gov",
                                      "WordPress. The survey recorded Benton as "
                                      "not-located; the tranche-2 hunt found the index "
                                      "IS the careers-and-benefits page. The ONA "
                                      "2025-2029 contract posted 2026-01 was unknown "
                                      "to the survey.")]),
        upstream="No feed; wp-content upload paths are dated by year/month, so new "
                 "uploads get new URLs — re-fetch the careers page and diff links.",
        header=["SURVEY CORRECTION: benton was `not-located` in the 2026-08-02 survey; "
                "this group upgrades it to verified — the index was one navigation "
                "level below where the search pass looked."]),
    "yamhill": dict(
        employer="yamhill-county", extractor=x_yamhill,
        title="Yamhill County union contracts",
        index="https://www.yamhillcounty.gov/300/Union-Contracts",
        crawl=dict(decision="proceed", checked=ARCHIVE_DATE,
                   basis="OPERATOR DECISION, recorded 2026-08-02: include Yamhill while it is "
                         "technically accessible to an honestly-identified agent. The facts the "
                         "decision weighed, kept on the record: yamhillcounty.gov serves the "
                         "Cloudflare-managed AI robots block (ClaudeBot/GPTBot/CCBot etc. get "
                         "Disallow: /) and User-agent: * carries Content-Signal: search=yes, "
                         "ai-train=no, use=reference (an EU DSM Art. 4 rights reservation). This "
                         "fetcher is none of the named agents and identifies itself honestly; "
                         "'use=reference' matches what this corpus does (summary-first, official "
                         "links); the oregon-counties precedent for this same host was also "
                         "proceed. The line that bounds the decision: technical access controls "
                         "are always respected — a WAF challenge or 403 makes that fetch "
                         "could-not-verify, never retried in disguise (the host 403'd the "
                         "survey's first pass and served the second, same UA — expect "
                         "intermittence). If the county ever tightens User-agent: * or names "
                         "this project, the decision is void and gets re-made, not inherited.",
                   hosts=[{"host": "www.yamhillcounty.gov",
                           "robots_url": "https://www.yamhillcounty.gov/robots.txt",
                           "ai_block": True,
                           "content_signal": "search=yes, ai-train=no, use=reference",
                           "notes": "Cloudflare managed AI-crawler block + content signals; "
                                    "User-agent: * is allowed. CivicPlus DocumentCenter links."}]),
        upstream="No feed; DocumentCenter slugs carry terms ('2024-to-2027-YCSO-CBA-PDF'), so an "
                 "index link-set diff is meaningful.",
        header=["The county budget book link on the same page is excluded (not a labor "
                "agreement)."]),
}


def _split(text: str) -> tuple[str, str]:
    """(comment header, yaml body) — the two halves this file is checked in."""
    lines = text.split("\n")
    i = 0
    while i < len(lines) and (lines[i].startswith("#") or not lines[i].strip()):
        i += 1
    return "\n".join(lines[:i]).strip(), "\n".join(lines[i:])


def _differs(committed: str, rendered: str) -> bool:
    """Would re-running discovery CHANGE WHAT THIS FILE SAYS?

    Not "produce identical bytes". `corpus-detect-changes --record-baseline` edits this
    file line by line to preserve its formatting, and writes `sha256: "abc..."` where
    `yaml.safe_dump` writes `sha256: abc...`. Identical YAML, different bytes -- and a byte
    comparison called all 12 groups STALE the day the baselines were seeded, pointing at a
    remedy that would have wiped them.

    The header IS compared verbatim, because it is prose this generator owns and the file
    says "do not hand-edit"; a byte-equal body is not the thing being protected there.
    """
    c_head, c_body = _split(committed)
    r_head, r_body = _split(rendered)
    if c_head != r_head:
        return True
    try:
        return yaml.safe_load(c_body) != yaml.safe_load(r_body)
    except yaml.YAMLError:
        return True


def _carry_recorded(county: str, sources: list[dict]) -> None:
    """Carry `sha256` (and its `last_checked`) across from the committed manifest.

    TWO WRITERS, ONE FILE, AND ONLY ONE OF THEM OWNS THIS FIELD. Discovery owns which
    documents exist -- ids, urls, titles, families. The BASELINE is owned by
    `corpus-detect-changes --record-baseline`, which records what upstream served so drift
    can be detected later.

    This renderer used to emit `sha256: ""` unconditionally, which made both halves wrong at
    once: `--check` byte-compares its output against the file, so every recorded baseline
    read as STALE -- and the remedy it printed, "re-run src/discover_counties.py", WIPED
    ALL 680 OF THEM. A stale-file message that tells you to destroy the data is worse than
    no message.

    A source discovery has never seen still starts empty; that is discovery's own field to
    set, and an unseeded source is reported by the drift run rather than hidden here.
    """
    out = SOURCES_DIR / f"{county}.yml"
    if not out.is_file():
        return
    try:
        held = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return
    prior = {s["id"]: s for s in (held.get("sources") or []) if isinstance(s, dict)}
    for s in sources:
        was = prior.get(s["id"])
        if not was:
            continue
        if was.get("sha256"):
            s["sha256"] = was["sha256"]
        if was.get("last_checked"):
            s["last_checked"] = was["last_checked"]


def render(county: str, cfg: dict, sources: list[dict]) -> str:
    n_cba = sum(1 for s in sources if s["family"] == "cba")
    n_loa = len(sources) - n_cba
    head = [
        "GENERATED by src/discover_counties.py from the archived survey fetch of "
        f"{ARCHIVE_DATE} — do not hand-edit; re-run it.",
        "Human-approved via PR BEFORE any ingestion (review gate #1).",
        f"Extracted from {cfg['index']}",
        f"({n_cba} cba, {n_loa} loa)",
        *cfg["header"],
    ]
    doc = {
        "group": county,
        "title": cfg["title"],
        "employer": cfg["employer"],
        "crawl": cfg["crawl"],
        "last_checked": ARCHIVE_DATE,
        "upstream_signal": cfg["upstream"],
        "sources": sources,
    }
    body = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
    return "".join(f"# {l}\n" if l else "#\n" for l in head) + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE,
                    help="directory of archived index fetches (default: the survey archive)")
    ap.add_argument("--only", metavar="COUNTY", help="regenerate a single county")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    failed = 0
    for county, cfg in COUNTIES.items():
        if args.only and county != args.only:
            continue
        page = (args.archive / f"{county}.html")
        if not page.is_file():
            print(f"ABORT {county}: no archived fetch at {page}", file=sys.stderr)
            failed += 1
            continue
        sources = cfg["extractor"](page.read_text(encoding="utf-8", errors="replace"))
        # Hand-verified additions living on OTHER domains than the county's index —
        # each carries its own provenance note (Jackson's ERB-exhibit JCSSA copy).
        sources += cfg.get("extra", [])
        if not sources:
            print(f"ABORT {county}: extractor found nothing — the page shape changed or the "
                  f"extractor broke; refusing to write an empty group", file=sys.stderr)
            failed += 1
            continue
        # Same-titled documents at different URLs are real upstream (Washington posts two
        # MOUs titled identically) — suffix deterministically rather than refuse.
        seen_ids: dict[str, int] = {}
        for s in sources:
            n = seen_ids.get(s["id"], 0)
            seen_ids[s["id"]] = n + 1
            if n:
                s["id"] = f"{s['id']}-{n + 1}"
        _carry_recorded(county, sources)
        text = render(county, cfg, sources)
        out = SOURCES_DIR / f"{county}.yml"
        if args.check:
            if not out.is_file() or _differs(out.read_text(encoding="utf-8"), text):
                print(f"{out.name} is STALE — re-run src/discover_counties.py", file=sys.stderr)
                failed += 1
            continue
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(REPO_ROOT)}: {len(sources)} source(s) "
              f"({sum(1 for s in sources if s['family'] == 'cba')} cba)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
