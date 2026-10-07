"""Roster-row title matching, shared by ingest_cbas.py and enumerate_cbas.py.

Deliberately dependency-free (stdlib only): the scheduled state-enumeration job
installs only pyyaml, so enumerate_cbas.py must not reach corpus_toolkit through
this module (oregon-collective-bargaining#107). Keep it that way.
"""
from __future__ import annotations


def matches_row(row: dict, title: str) -> bool:
    """A title names this roster row's unit when it carries `match` (the
    current-term title) OR, if the row has one, `predecessor_match` -- the
    explicit id-override option from the KNOWN GAPS: THE PAIRING GAP note in
    src/ingest_cbas.py's module docstring, for a unit whose roster row was
    renamed to the current term's title wording and no longer matches its own 2023-2025 predecessor's older title. Either
    string is still subject to the row's `exclude`."""
    if row.get("exclude") and row["exclude"] in title:
        return False
    predecessor_match = row.get("predecessor_match")
    return row["match"] in title or bool(predecessor_match and predecessor_match in title)
