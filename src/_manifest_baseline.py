"""Shared plumbing between `src/enumerate_cbas.py` and `src/discover_counties.py`:
both generators rewrite a source manifest group wholesale and must carry a recorded
`sha256` baseline across the rewrite without disturbing it.

TWO WRITERS, ONE FIELD, PER MANIFEST FILE. A generator owns which documents exist --
ids, urls, titles, families -- re-derived fresh every run. The BASELINE is owned by
`corpus-detect-changes --record-baseline`, which records what upstream served so
drift can be detected later; a generator's own `build_sources()`/extractor always
emits `sha256: ""` because it has no way to know that value and must not guess it.

Carried on **`url`**, not `id` (oregon-collective-bargaining#14's Agent Brief:
"preserve an existing `sha256` for a source whose `url` is unchanged" -- and its join
hazard note: "`source_url` is the reliable key"). `id` is a slug derived from a
filename or title and can move independently of the underlying document: a file
relocated inside its library keeps its old slug but is a different fetch and must not
inherit that fetch's baseline, and two differently-named files can slug to the same
id and silently collapse in an id-keyed dict. Keying on `url` avoids both failure
modes: a rename at an unchanged url still carries; a file moved to a new url starts
unseeded, same as any source no baseline has ever been recorded for.

`last_checked` is deliberately NOT carried here -- see the #14 code review that
introduced this module. The state-tier generator used to carry it, which froze the
enumeration date at its first-seeded value forever for every previously-seeded
source, directly contradicting `enumerate_cbas._strip_dates`'s own documented
contract that `last_checked` "moves on every run by design". Only `sha256` is a
value worth protecting from a rewrite; `last_checked` is enumeration/discovery's own
field, and a generator should say plainly when it last looked, not when it first did.
"""
from __future__ import annotations


class Quoted(str):
    """A string this file writes in double quotes.

    ONE FILE, TWO WRITERS, AND THEY DISAGREE ABOUT QUOTING UNLESS TOLD OTHERWISE.
    `corpus-detect-changes --record-baseline` edits a manifest line by line and
    writes `sha256: "abc..."`; `yaml.safe_dump` on a plain str writes
    `sha256: abc...`. Identical YAML, different bytes -- and a real diff arrives
    buried in quote churn the moment the other tool touches the file next.
    """


def quoted_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


def carry_recorded_sha256(committed_sources: list, sources: list) -> None:
    """Mutate `sources` in place: for each entry whose `url` matches an entry in
    `committed_sources` that already carries a non-empty `sha256`, wrap that value
    in `Quoted` and copy it across. A source no committed entry's `url` matches is
    left exactly as the caller's own builder produced it -- an unseeded source is
    the drift job's field to fill via `--record-baseline`, never this function's to
    invent or infer.
    """
    prior = {s["url"]: s for s in committed_sources
             if isinstance(s, dict) and s.get("url")}
    for s in sources:
        was = prior.get(s.get("url"))
        if was and was.get("sha256"):
            s["sha256"] = Quoted(was["sha256"])
