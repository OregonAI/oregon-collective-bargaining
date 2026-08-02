#!/usr/bin/env python3
"""Second-engine corroboration for OCR'd scans, per the platform's two-engine rule.

The rule lives in `oregon-policy-repo/AGENTS.md`; the reference implementations are
that repo's `src/ocr_fallback_eo.py` and `oregon-kpm/src/ocr_corroborate.py`. This
module is the SAME CONTRACT as the kpm one — same 0.80 agreement bar, same quality
gate, same `conversion_notes` wording, same engine pair — with this corpus's paths
and vocabulary source. It exists rather than being imported because the corpora
share no code path (kpm's lesson, kept).

WHY A SECOND ENGINE AT ALL. Mostly-right text is the dangerous case, because it
reads as authoritative. One engine's output is unverifiable: there is nothing to
check it against. Two engines that share no model weights are vanishingly unlikely
to invent the SAME words, so high agreement is positive evidence the words are
physically on the page.

THE PAIR IS tesseract + PaddleOCR, the pair kpm measured (0.816-0.929 agreement on
its six scans; docTR is the tiebreaker there, not the default, and the same applies
here). PaddleOCR reads the ORIGINAL scan, so the engines share nothing but pixels.

ONE RULE THIS CORPUS ADDS ON TOP: `references_external` stays WITHHELD on OCR
documents regardless of score. kpm's measurement is the reason — figure agreement
runs 3-9 points below word agreement because digits are exactly where engines
diverge — and here a misread digit would not just misreport a number, it would
resolve a citation to the WRONG STATUTE while looking cited. Figure agreement is
disclosed in conversion_notes, per the kpm wording; it is not a license.

WHAT AGREEMENT DOES NOT PROVE. It is evidence the words are on the page. It is NOT
evidence they were read correctly, and it says nothing about figures — two engines
can misread the same smudged digit the same way. Every number in an OCR'd document
stays unverified against the source, which is why `conversion_notes` ends
"NOT human-verified".
"""
from __future__ import annotations

import difflib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "_meta" / "snapshots"
AGREEMENTS = ROOT / "agreements"

MIN_AGREEMENT = 0.80
MIN_DICT_RATIO = 0.80
MIN_WORDS = 100

ENGINES = ("tesseract (ocrmypdf)", "paddleocr PP-OCRv6")

WORD = re.compile(r"[a-z]{2,}")
# A reported figure: percentage, currency, count, ratio. Matched loosely on purpose —
# the question is whether the two engines read the same characters.
FIGURE = re.compile(r"\$?-?\d[\d,]*(?:\.\d+)?%?")

_VOCAB: set[str] | None = None
_PADDLE = None


def vocabulary() -> set[str]:
    """Dictionary for the quality gate, built from THIS corpus's own non-OCR text.

    /usr/share/dict/words is absent on this host, and a general wordlist is a poor
    fit for labor-agreement prose anyway ("recoupment", "griev", unit acronyms). The
    snapshots whose text came from a real text layer are the right reference: same
    register, same corpus. OCR'd snapshots are EXCLUDED, and the exclusion is the
    whole point — kpm's first measured result was six documents scoring 100%
    dictionary-recognizable because the OCR errors had entered the vocabulary that
    judged them. A gate that cannot fail is worse than no gate."""
    global _VOCAB
    if _VOCAB is not None:
        return _VOCAB
    ocr_ids = set()
    for md in AGREEMENTS.rglob("*.md"):
        head = md.read_text(encoding="utf-8", errors="replace").split("---", 2)
        if len(head) >= 3 and re.search(r"^text_source:\s*ocr\s*$", head[1], re.M):
            ocr_ids.add(md.stem)
    files = sorted(p for p in SNAPSHOTS.glob("*.txt") if p.stem not in ocr_ids)
    # Sampled evenly across the sorted set rather than the first N — an arbitrary
    # slice skews the vocabulary toward whichever employers sort first (kpm's note).
    step = max(1, len(files) // 400)
    vocab: set[str] = set()
    for p in files[::step]:
        vocab |= set(WORD.findall(p.read_text(encoding="utf-8", errors="replace").lower()))
    _VOCAB = vocab
    return vocab


def paddle_text(pdf_path: Path, workdir: Path) -> str | None:
    """PaddleOCR over the ORIGINAL scan. None if PaddleOCR is unavailable.

    Orientation classification is ON — kpm measured 0.050 vs 0.929 agreement on the
    same rotated page with it off vs on; that number measures the configuration,
    not the page."""
    global _PADDLE
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        return None
    workdir.mkdir(parents=True, exist_ok=True)
    for old in workdir.glob("*.png"):
        old.unlink()
    try:
        subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf_path), str(workdir / "p")],
                       check=True, capture_output=True, timeout=1800)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    if _PADDLE is None:
        _PADDLE = PaddleOCR(lang="en", use_doc_orientation_classify=True,
                            use_doc_unwarping=False, use_textline_orientation=True)
    out: list[str] = []
    for img in sorted(workdir.glob("p-*.png")):
        for d in _PADDLE.predict(str(img)):
            out.extend(d.get("rec_texts") or [])
    return "\n".join(out)


def score(primary: str, cross_check: str, vocab: set[str]) -> dict:
    """Quality of the text that would be committed, and its agreement with the second
    engine. Identical metric set to the kpm reference."""
    wa = WORD.findall(primary.lower())
    wb = WORD.findall(cross_check.lower())
    ratio = sum(1 for w in wa if w in vocab) / len(wa) if wa else 0.0
    agreement = (difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio()
                 if wa and wb else 0.0)
    # Glued heading/letterhead tokens: counted so they can be disclosed, deliberately
    # not repaired — re-inserting word boundaries would be writing text the OCR did
    # not resolve.
    glued = len(re.findall(r"\b[A-Za-z]{18,}\b", primary))
    fa = FIGURE.findall(primary.lower())
    fb = FIGURE.findall(cross_check.lower())
    fig = (difflib.SequenceMatcher(None, fa, fb, autojunk=False).ratio()
           if fa and fb else 0.0)
    return {"words": len(wa), "dict_ratio": ratio, "agreement": agreement, "glued": glued,
            "figures": len(fa), "figure_agreement": fig,
            "gate_ok": len(wa) >= MIN_WORDS and ratio >= MIN_DICT_RATIO,
            "agree_ok": agreement >= MIN_AGREEMENT}


def notes(s: dict) -> str:
    """The `conversion_notes` string. Wording matches the reference implementations."""
    glued_note = (f"; {s['glued']} heading/letterhead token(s) lost their word spacing in "
                  f"extraction and are left as-is rather than reconstructed"
                  if s["glued"] else "")
    return (f"no text layer in the source PDF; text recovered by OCR. Two independent "
            f"engines ({' + '.join(ENGINES)}) agree on {s['agreement']:.0%} of the word "
            f"sequence and {s['figure_agreement']:.0%} of the {s['figures']} figures, "
            f"{s['dict_ratio']:.0%} dictionary-recognizable{glued_note}; "
            f"NOT human-verified — treat every number as unchecked against the source")
