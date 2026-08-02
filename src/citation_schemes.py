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


# The term inside a document id ("...-2025-2027" — also mid-id for the blackline,
# whose id ends with its as-of date instead). Date fragments like 02202026 have no
# hyphen and cannot false-match.
_TERM_IN_ID = re.compile(r"20\d{2}-20\d{2}")


def _id_term(doc_id: str) -> str:
    mm = _TERM_IN_ID.search(doc_id)
    return mm.group(0) if mm else ""


def _resolve_cba(m: re.Match, nodes: dict) -> tuple[list, str | None]:
    union = _UNION_SLUG[m["union"].lower()]
    term = m["term"].replace("–", "-") if m["term"] else None
    employer = m["employer"].lower().replace(" ", "-") + "-county" if m["employer"] else None

    # A document id carries the union as its acronym OR its full name slugified —
    # DAS names ONA's file "Oregon Nurses Association 2025-2027" with no acronym, so
    # `state-oregon-nurses-association-2025-2027` must still resolve as ONA. Generic
    # single words ("nurses") are deliberately NOT fragments: "-nurses-" also appears
    # in AFSCME's OSH Registered Nurses unit and would cross the union boundary.
    fragments = {union} | {"ona": {"oregon-nurses-association"},
                           "iuoe": {"operating-engineers"}}.get(union, set())
    hits = []
    for doc_id in nodes:
        padded = f"-{doc_id}-"
        if not any(f"-{f}-" in padded for f in fragments):
            continue
        if "-loa-" in doc_id:
            continue                       # letters resolve via their own citations
        if employer and not doc_id.startswith(employer):
            continue
        hits.append(doc_id)

    # Unit words between the union and the tail word narrow multi-unit unions —
    # AFSCME signs 24 state units per term, so union+term alone is NOT unique and
    # returning one silently would be exactly the wrong-answer shape this corpus
    # exists to prevent. DAS filenames (and so ids) spell units out, so an acronym
    # qualifier ("DEQ") may not narrow; that case gets a note, never a guess —
    # the acronym→unit crosswalk is later work, recorded, not improvised here.
    stop = {"the", "of", "and", "a", "an", "state", "county", "local", "no"}
    tokens = [t for t in re.findall(r"[a-z0-9]+", (m["unit"] or "").lower())
              if t not in stop]
    unit_note = None
    if tokens:
        narrowed = [d for d in hits if all(t in d for t in tokens)]
        if narrowed:
            hits = narrowed
        else:
            unit_note = (f"qualifier {' '.join(tokens)!r} matched no held unit name — "
                         f"unit names are spelled out (DAS filenames), so an acronym "
                         f"may not narrow; all {m['union']} matches returned")

    def _drafted(note: str | None, ids: list) -> str | None:
        # A draft print (the SEIU blackline) resolving without a warning would be
        # the executed-text assumption this corpus refuses to make.
        if any("blackline" in d for d in ids):
            extra = ("includes a blackline/draft print — check the document's "
                     "status; it is NOT the executed text")
            return f"{note}; {extra}" if note else extra
        return note

    if term:
        exact = [d for d in hits if _id_term(d) == term]
        if not exact:
            return [], (f"no {m['union']} agreement with term {term} is held; terms present: "
                        + (", ".join(sorted(_id_term(d) or "undated" for d in hits)) or "none"))
        if len(exact) > 1:
            note = (f"{len(exact)} {m['union']} agreements share term {term} (one per "
                    f"bargaining unit)" + (f"; {unit_note}" if unit_note else
                    "; add unit words to pin one"))
            return exact, _drafted(note, exact)
        return exact, _drafted(unit_note, exact)

    # Bare citation: newest term first, ambiguity stated.
    hits.sort(key=_id_term, reverse=True)
    note = None
    if len(hits) > 1:
        note = (f"'{m.group(0).strip()}' names no term"
                + ("" if employer else " or employer")
                + f"; {len(hits)} agreements match — newest term first, and expired "
                  "terms may follow. Cite union + term (+ county) to pin one.")
    return hits, _drafted(note, hits)


# One scheme, three citation shapes: "[term] [county [County]] <UNION> ... agreement".
# The tail word is required — bare "SEIU" in running text is a mention, not a citation.
register_scheme(
    "cba-agreement",
    rf"(?i)(?:(?P<term>20\d{{2}}\s*[-–]\s*20\d{{2}})\s+)?"
    rf"(?:(?P<employer>{_EMPLOYER_WORDS})\s+(?:county(?:'s)?\s+)?)?"
    rf"(?P<union>{_UNION_ALT})\b[\s,]*(?P<unit>[^.;]{{0,40}}?)\s*"
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
