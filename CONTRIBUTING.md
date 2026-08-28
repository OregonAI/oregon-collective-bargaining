# Contributing

All changes via PR with CODEOWNER review. Before merge, the PR checklist
requires: pinned source URL reachable; retrieval date + hash recorded;
version/effective dates transcribed exactly as the source prints them;
`## Full text` verified verbatim (CI-diffed); relationships resolve;
disclaimer present; CHANGELOG updated. Reviewers set `last_verified` /
`verified_by` at approval. Agent-assisted commits carry an
`Assisted-by:` trailer.

## Running tests

`tests/` holds this repo's Python unit test suite (currently: the manifest
generators' baseline-carrying logic — see `tests/test_enumerate_cbas.py` and
`tests/test_discover_counties.py`). Run it locally with:

```
pip install -r requirements.txt -r requirements-dev.txt
python3 -m pytest tests/ -q
```

Gated on every PR by the `tests` job in `.github/workflows/ci.yml`.
