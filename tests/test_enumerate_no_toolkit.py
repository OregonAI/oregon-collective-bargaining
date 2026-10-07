"""oregon-collective-bargaining#107: the scheduled state-enumeration job installs
only pyyaml, so `src/enumerate_cbas.py` must not import corpus_toolkit, directly or
through another src/ module (PR #106 regressed this by importing ingest_cbas for
`matches_row()`). One `matches_row()` implementation, in a dependency-free module,
is shared by enumerate_cbas and ingest_cbas."""
import subprocess
import sys
import textwrap
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

BLOCK_TOOLKIT = textwrap.dedent("""
    import sys
    class _Block:
        def find_spec(self, name, path=None, target=None):
            if name == "corpus_toolkit" or name.startswith("corpus_toolkit."):
                raise ImportError("corpus_toolkit is not installed (pyyaml-only job)")
    sys.meta_path.insert(0, _Block())
    sys.path.insert(0, %r)
""" % str(SRC))


def _run(code: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", BLOCK_TOOLKIT + textwrap.dedent(code)],
                          capture_output=True, text=True)


def test_enumerate_cbas_imports_without_corpus_toolkit():
    r = _run("import enumerate_cbas")
    assert r.returncode == 0, r.stderr


def test_enumerate_cbas_does_not_load_corpus_toolkit_transitively():
    r = _run("""
        import enumerate_cbas
        assert not [m for m in sys.modules if m.split(".")[0] == "corpus_toolkit"]
    """)
    assert r.returncode == 0, r.stderr


def test_reconcile_runs_without_corpus_toolkit():
    r = _run("""
        import enumerate_cbas
        roster = {"term": "2025-2027", "state_contracts": [
            {"unit": "U", "match": "Widgets", "ratified": None}],
            "non_state_contracts": []}
        enumerate_cbas.reconcile([{"Name": "Widgets 2025-2027.pdf"}], roster)
    """)
    assert r.returncode == 0, r.stderr


def test_ingest_and_enumerate_share_one_matches_row():
    import cba_matching
    import ingest_cbas
    import enumerate_cbas
    assert ingest_cbas.matches_row is cba_matching.matches_row
    assert enumerate_cbas.matches_row is cba_matching.matches_row
