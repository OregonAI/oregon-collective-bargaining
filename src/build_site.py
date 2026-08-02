#!/usr/bin/env python3
"""Build the GitHub Pages site into ./site/ (gitignored; produced at deploy time).

    python3 src/build_site.py

Chrome, CSS and the cross-corpus contracts live in `corpus_toolkit.site`. This file
owns only what is specific to this corpus: its numbers and what they mean.

THIS REPLACES the reusable publish-index workflow (which publishes corpus-index.json
and nothing else — the 404-at-root arrangement). The two must never both exist here;
they fight over the `pages` concurrency group. corpus-index.json keeps emitting at
the same URL — siblings resolve citations into this corpus through it.
"""
import collections
import json
import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from corpus_toolkit import config as config_mod                       # noqa: E402
from corpus_toolkit.site import Page, Section, Tile, build            # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent


def stats() -> dict:
    status = collections.Counter()
    ocr = 0
    for p in (REPO / "agreements").rglob("*.md"):
        fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1]) or {}
        status[fm.get("status", "?")] += 1
        if fm.get("text_source") == "ocr":
            ocr += 1
    emp = yaml.safe_load((REPO / "_meta/employers.yml").read_text())["employers"]
    surv = collections.Counter(e["survey_status"] for e in emp if e["kind"] == "county")
    g = json.loads((REPO / "_meta/graph.json").read_text())
    outbound = sum(1 for e in g["edges"]
                   if e["to"].split()[0] in ("ORS", "OAR"))
    return {"docs": g["n_nodes"], "current": status["current"],
            "superseded": status["superseded"], "draft": status["draft"], "ocr": ocr,
            "built": sum(1 for e in emp if e["built"]),
            "employers": len(emp), "outbound": outbound,
            "cnv": surv["could-not-verify"], "nloc": surv["not-located"],
            "ninv": surv["not-investigated"]}


def main() -> int:
    s = stats()
    out = build(Page(
        config=config_mod.load(REPO / "_meta/corpus.yml"),
        repo="oregon-collective-bargaining",
        title="Oregon Collective Bargaining — State and County Labor Agreements",
        description=("A non-authoritative, summary-first mirror of the collective "
                     "bargaining agreements of Oregon state government and Oregon "
                     "counties."),
        eyebrow="Oregon · Negotiated agreements — contracts, not law",
        headline="The contracts that govern Oregon's public workforce",
        lede_html=(
            f"<b>{s['docs']} agreements and letters</b> across {s['built']} public "
            f"employers — the State of Oregon (DAS bargains 35 contracts across 12 "
            f"unions) and the counties that publish their labor agreements. "
            f"<b>Summary-first:</b> this corpus records what each agreement is, its "
            f"term, and where the official text lives — it does not reproduce the "
            f"text."),
        disclaimer=("NON-AUTHORITATIVE reference — never the agreement's text. Always "
                    "verify at the official source linked on every document."),
        tiles=[
            Tile("Agreements held", f"{s['docs']}",
                 f"{s['current']} current · {s['superseded']} superseded · "
                 f"{s['draft']} draft"),
            Tile("Employers covered", f"{s['built']}",
                 f"of {s['employers']} in the registry (the state + 36 counties)"),
            Tile("Statute citations", f"{s['outbound']}",
                 "ORS/OAR cited by agreement text — cites, never implements"),
        ],
        sections=[
            Section("A contract is not a statute", """
    <ul class="plain">
      <li><b>This corpus sits outside the authority chain.</b> A collective bargaining
        agreement is a negotiated contract; it implements nothing, and no document here
        asserts an <code>implements</code> edge. Statutes an agreement cites (ORS 243
        in recognition clauses) resolve into
        <a href="https://oregonai.github.io/executive-regulatory-frameworks/">Executive
        Regulatory Frameworks</a> as citations.</li>
      <li><b>Summary-first, by recorded decision.</b> A CBA is jointly authored with
        private parties, and "public record" and "freely reproducible" are not the same
        claim. Every document carries its <code>reproduction_basis</code> and the
        official link.</li>
      <li><b>Expired ≠ absent; current ≠ assumed.</b> Agreements run in terms and
        expire; superseded agreements stay, marked; a ratified-but-unposted successor
        is named where DAS has not yet posted the executed text.</li>
    </ul>"""),
            Section("Coverage, honestly", f"""
    <ul class="plain">
      <li>{s['built']} employers have documents. Among counties without them:
        {s['cnv']} refused an honestly-identified fetcher (a fact about our access),
        {s['nloc']} have no locatable public index, and {s['ninv']} were not yet
        investigated — <b>these are different sentences about Oregon</b> and are never
        summed. The registry (<code>_meta/employers.yml</code>) carries each verdict.</li>
      <li>{s['ocr']} documents' text came from two-engine corroborated OCR of
        image-only scans — each says so, with both engines' agreement rates, and none
        of them contributes statute citations (digits are where engines diverge).</li>
    </ul>"""),
            Section("For agents", """
    <ul class="plain">
      <li><b>MCP server</b> — tools: <code>search_corpus</code>,
        <code>get_document</code>, <code>resolve_citation</code> (try
        "2025-2027 AFSCME Building Codes agreement" — bare forms return every match
        with the ambiguity stated), <code>corpus_overview</code>,
        <code>graph_neighbors</code>.</li>
      <li><b>Every document carries provenance</b> — source URL, retrieval date, a
        content hash over the committed extraction, and its term and expiry.</li>
    </ul>"""),
        ],
        footer_note=("Unofficial and non-authoritative; not affiliated with the State "
                     "of Oregon, DAS, any county, or any labor organization."),
    ))
    print(f"built site/ — {s['docs']} documents, {s['built']} employers")
    print(f"  corpus-index.json: {out['index']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
