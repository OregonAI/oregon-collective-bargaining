# Discovery evidence

Byte-for-byte archived fetches of each county's labor-agreements index page (and
each document host's robots.txt), made 2026-08-02 with the platform's honest
User-Agent during the seed survey (timestamps in `fetch-started.txt` /
`fetch-finished.txt`; HTTP status log in `results.txt`; the full survey lives at
`corpus-seeds/oregon-collective-bargaining.survey.yml` in the operator's seeds
collection).

`src/discover_counties.py` parses THESE files — never a live page — so
`_meta/sources/<county>.yml` is reproducible in CI and every source row traces to
a page a reviewer can open. To re-discover: fetch fresh copies into a new dated
directory, update the script's `DEFAULT_ARCHIVE`/`ARCHIVE_DATE`, and re-run; the
old directory stays as the record of what the county published when.
