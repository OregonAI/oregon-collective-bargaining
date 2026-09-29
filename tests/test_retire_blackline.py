"""The SEIU blackline's banner promised it would be superseded "the day the final
appears". retire_blackline() is that promise, run by ingest_cbas.py on every ingest."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import ingest_cbas  # noqa: E402

BL = "state-seiu-2025-2027-blackline-as-of-02202026"
FINAL = "state-seiu-master-agreement-collective-bargaining-agreement-2025-2027"
PRIOR = "state-seiu-master-agreement-collective-bargaining-agreement-2023-2025"


def _doc(d: Path, doc_id, title, term, status, body="\nbody\n"):
    fm = {"id": doc_id, "title": title, "term": term, "status": status,
          "relationships": {"related": [], "supersedes": []}}
    (d / f"{doc_id}.md").write_text("---\n" + yaml.safe_dump(fm, sort_keys=False)
                                    + "---\n" + body, encoding="utf-8")


def _fm(d: Path, doc_id):
    return yaml.safe_load((d / f"{doc_id}.md").read_text().split("---\n", 2)[1])


def _corpus(tmp_path, monkeypatch, with_final):
    monkeypatch.setattr(ingest_cbas, "OUT_DIR", tmp_path)
    _doc(tmp_path, BL, "SEIU 2025-2027 Blackline as of 02202026", "2025-2027", "draft",
         "\n" + ingest_cbas.DRAFT_BANNER + "\n")
    _doc(tmp_path, PRIOR, "SEIU Master Agreement Collective Bargaining Agreement 2023-2025",
         "2023-2025", "superseded")
    if with_final:
        _doc(tmp_path, FINAL, "SEIU Master Agreement Collective Bargaining Agreement 2025-2027",
             "2025-2027", "current")


def test_nothing_changes_until_the_executed_final_exists(tmp_path, monkeypatch):
    _corpus(tmp_path, monkeypatch, with_final=False)
    assert ingest_cbas.retire_blackline() == []
    assert _fm(tmp_path, BL)["status"] == "draft"


def test_the_final_retires_the_blackline_and_supersedes_both(tmp_path, monkeypatch):
    _corpus(tmp_path, monkeypatch, with_final=True)
    assert set(ingest_cbas.retire_blackline()) == {BL, FINAL}
    assert _fm(tmp_path, BL)["status"] == "superseded"
    body = (tmp_path / f"{BL}.md").read_text()
    assert "DRAFT PRINT" not in body and f"`{FINAL}`" in body
    assert _fm(tmp_path, FINAL)["relationships"]["supersedes"] == sorted([BL, PRIOR])


def test_it_is_idempotent(tmp_path, monkeypatch):
    _corpus(tmp_path, monkeypatch, with_final=True)
    ingest_cbas.retire_blackline()
    before = {p.name: p.read_text() for p in tmp_path.glob("*.md")}
    assert ingest_cbas.retire_blackline() == []
    assert before == {p.name: p.read_text() for p in tmp_path.glob("*.md")}
