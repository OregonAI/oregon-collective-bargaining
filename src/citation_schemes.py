#!/usr/bin/env python3
"""Citation schemes this corpus resolves, registered with the MCP framework.

Loaded via `plugins.citation_module` in _meta/corpus.yml. Importing this module is
the whole contract — `register_scheme` calls happen at import time.

HOW CBAs ARE ACTUALLY CITED (the seed's finding): by union + term ("the 2023-2025
SEIU 503 agreement, Article 45"), by employer + union ("Multnomah's AFSCME Local 88
contract"), and — constantly — by the bare form ("the SEIU contract"). The bare form
is genuinely ambiguous TWICE OVER: across terms (2023-2025 vs 2025-2027) and across
employers (SEIU 503 signs the state master, Marion's MCEA and Jackson's association).
The scheme therefore behaves like the legislature's bare bill numbers: with no term
given it returns every matching agreement NEWEST TERM FIRST with the ambiguity stated
in the note, never a silent guess. Article-level slicing is a snapshot_slice concern,
not a resolution concern — resolution lands on the agreement document.

DOCUMENT ID CONVENTION this resolves against (fixed here, before ingest, so the
ingester and the scheme cannot drift apart):

    <employer-slug>-<union-or-unit-slug>-<term>          e.g.
    state-seiu-503-master-2025-2027
    multnomah-county-afscme-local-88-2025-2028
    ...and LOAs:  <employer-slug>-<union-slug>-loa-<subject-slug>

Resolution is a scan over node ids (resolver(match, nodes) — the framework passes the
corpus graph), which means it needs NO hand-maintained table of agreements: a new
term's document starts resolving the day it is ingested.

REGISTER_SCHEME COMPILES WITH NO FLAGS — every pattern spells out its own case
handling (the oregon-records-retention lesson, inherited via oregon-audits).
"""
import re

from corpus_toolkit.mcp.framework import register_scheme

# Union/association tokens an agreement citation actually uses, mapped to the slug
# fragment that appears in document ids. Big statewide names plus the county
# associations the ten verified county pages name today; extend as counties ingest.
_UNION_SLUG = {
    "seiu": "seiu", "afscme": "afscme", "ona": "ona",
    "oregon nurses association": "ona", "nurses": "ona",
    "aee": "aee", "foppo": "foppo", "aoce": "aoce", "cia": "cia",
    "opsa": "opsa", "ospoa": "ospoa", "stea": "stea", "iaff": "iaff",
    "teamsters": "teamsters", "ibew": "ibew", "iuoe": "iuoe",
    "operating engineers": "iuoe",
    "ccpoa": "ccpoa", "ccea": "ccea", "wcpoa": "wcpoa", "wcpaa": "wcpaa",
    "mcea": "mcea", "mclea": "mclea", "mcdaa": "mcdaa", "mcjea": "mcjea",
    "mcssa": "mcssa", "jcsea": "jcsea", "ycea": "ycea", "ycso": "ycso",
    "ycddaa": "ycddaa", "ycjdwa": "ycjdwa", "dcsea": "dcsea", "dcdaa": "dcdaa",
    "lcpoa": "lcpoa", "cads": "cads", "ccdsa": "ccdsa", "ccsa": "ccsa",
}
_UNION_ALT = "|".join(sorted((re.escape(k) for k in _UNION_SLUG), key=len, reverse=True))

# Employer words a citation might carry. "state" is implied by DAS/state/master;
# county citations name the county. Slugs match _meta/employers.yml.
_EMPLOYER_WORDS = (
    "baker|benton|clackamas|clatsop|columbia|coos|crook|curry|deschutes|douglas|"
    "gilliam|grant|harney|hood river|jackson|jefferson|josephine|klamath|lake|lane|"
    "lincoln|linn|malheur|marion|morrow|multnomah|polk|sherman|tillamook|umatilla|"
    "union|wallowa|wasco|washington|wheeler|yamhill"
)


def _resolve_cba(m: re.Match, nodes: dict) -> tuple[list, str | None]:
    union = _UNION_SLUG[m["union"].lower()]
    term = m["term"].replace("–", "-") if m["term"] else None
    employer = m["employer"].lower().replace(" ", "-") + "-county" if m["employer"] else None

    hits = []
    for doc_id in nodes:
        if f"-{union}-" not in f"-{doc_id}-":
            continue
        if "-loa-" in doc_id:
            continue                       # letters resolve via their own citations
        if employer and not doc_id.startswith(employer):
            continue
        hits.append(doc_id)

    if term:
        exact = [d for d in hits if d.endswith(term)]
        if exact:
            return exact, None
        return [], (f"no {m['union']} agreement with term {term} is held; terms present: "
                    + (", ".join(sorted({d[-9:] for d in hits})) or "none"))

    # Bare citation: newest term first, ambiguity stated. Sorting by the trailing
    # YYYY-YYYY works because the id convention pins the term at the end.
    hits.sort(key=lambda d: d[-9:], reverse=True)
    note = None
    if len(hits) > 1:
        note = (f"'{m.group(0).strip()}' names no term"
                + ("" if employer else " or employer")
                + f"; {len(hits)} agreements match — newest term first, and expired "
                  "terms may follow. Cite union + term (+ county) to pin one.")
    return hits, note


# One scheme, three citation shapes: "[term] [county [County]] <UNION> ... agreement".
# The tail word is required — bare "SEIU" in running text is a mention, not a citation.
register_scheme(
    "cba-agreement",
    rf"(?i)(?:(?P<term>20\d{{2}}\s*[-–]\s*20\d{{2}})\s+)?"
    rf"(?:(?P<employer>{_EMPLOYER_WORDS})\s+(?:county(?:'s)?\s+)?)?"
    rf"(?P<union>{_UNION_ALT})\b[^.;]{{0,40}}?"
    rf"(?:agreement|contract|cba|master)",
    resolver=_resolve_cba,
)

# ---------------------------------------------------------------- outbound: ERF
#
# CBAs cite state law — PECBA (ORS 243) in recognition and grievance articles, agency
# statutes in scope clauses — as references_external, never implements (the corpus
# sits outside the authority chain by design; see corpus.yml). Patterns and the
# lettered-chapter lowercasing are copied from oregon-audits, which paid for them
# (its issue #81: uppercase 163A resolved to nothing while ERF held 285 sections).
register_scheme("ors-section", r"ORS\s+(?P<num>\d+[A-Z]?\.\d{3,})",
                resolver=lambda m: [f"ors-{m['num'].lower()}"],
                corpus="executive-regulatory-frameworks")
register_scheme("oar-rule", r"OAR\s+(?P<num>\d{3}-\d{3}-\d{4})",
                "oar-{num}", corpus="executive-regulatory-frameworks")
