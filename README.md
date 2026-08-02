# Oregon Collective Bargaining — State and County Labor Agreements

> ## ⚠️ NON-AUTHORITATIVE — AI-friendly reference only
> Curated copies/summaries, not official text. Always verify at the
> authoritative source linked in each document. See [DISCLAIMER.md](DISCLAIMER.md).

Part of the OregonAI civic corpus platform
([reference architecture](https://github.com/OregonAI/corpus-toolkit)).
Archetype: **document**. MCP interface: contract v1.

The collective bargaining agreements of Oregon's public employers — the state
workforce (DAS Labor Relations bargains 35 contracts across 12 unions, plus five
non-state units) and the 36 counties (each publishing, or not publishing, its own
labor agreements) — plus the letters of agreement that amend them mid-term. A new
instrument family for the platform: **negotiated contracts, not law**. This corpus
deliberately sits outside the authority chain — no `implements` claims against
ORS/OAR — and joins the platform through employers instead (the ERF agency registry
for state agreements, the county registry for county ones).

Seed and measured source survey: `corpus-seeds/oregon-collective-bargaining.md` /
`.survey.yml` in the operator's seeds collection (PLAN.md Phase 13).

| Entry point | For |
|---|---|
| [llms.txt](llms.txt) | Machine-readable index — AI agents start here |
| [AGENTS.md](AGENTS.md) | Agent rules and anti-fabrication requirements |
| [STATUS.md](STATUS.md) | Generated health: freshness, coverage, drift |
| `_meta/corpus.yml` | Corpus configuration |
| `_meta/employers.yml` | The employer registry: the state + all 36 counties, with each survey status |
| `_meta/sources/` | Per-employer source groups (human gate #1 — approved before any ingestion) |

## Two disciplines specific to this corpus

- **Summary-first until the copyright determination.** A CBA is jointly authored
  with private parties; "public record" and "freely reproducible" are not the same
  claim. `content_mode: summary` with official links is the default
  (`schema.doc_types` sets `verbatim: false`); each document records its
  `reproduction_basis`.
- **Expired ≠ absent; current ≠ assumed.** Agreements run in terms and expire;
  successors supersede predecessors. Every document carries `term`/`expiry_date`,
  and a superseded agreement stays in the corpus, marked superseded.

## License
Content (curated government material): CC0-1.0. Tooling, structure,
metadata: MIT. See [LICENSE](LICENSE).
