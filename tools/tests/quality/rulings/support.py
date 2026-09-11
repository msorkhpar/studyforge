"""The synthetic record every `tools.quality.rulings` test builds its tree from.

⭐ **One minimally-inhabited pair of records, and every control is that pair with
one thing moved** — a forward reference, a declaration, a number outside the
series. ⛔ Shared machinery, so `config.TEST_SUPPORT_NAMES` exempts it from
R12's mirror.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.rulings.derive import RECORD_DIR

#: Two rulings with a subject heading each — the shape 186 of the 197 real rows
#: have, so a test that passes here is testing the common case rather than a
#: curiosity.
ROUND_14 = """# CTO — round 14

## ⛔ Ruling 1 — the first thing, settled

Prose about the first thing.

## ⛔ Ruling 2 — the second thing, settled

Prose about the second thing.
"""


def write(root: Path, name: str, text: str) -> Path:
    """Put `text` at `RECORD_DIR/name` under a temporary repository root."""
    path = root / RECORD_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def record(round_number: int) -> str:
    """The filename a record of `round_number` must have to be read at all."""
    return f"CTO-2026-09-10-round{round_number}.md"


def tree(root: Path, **rounds: str) -> Path:
    """Build a temporary repository holding one record per keyword, `r14=…` style."""
    for key, text in rounds.items():
        write(root, record(int(key.lstrip("r"))), text)
    return root
