"""Mirror of `tools/quality/rulings/__main__.py` (R12).

⛔ **Both exit codes are inhabited**, and the write arm is asserted by reading
back what it wrote: a generator whose `--check` passes because it regenerated on
the way past would be a check that cannot fail.
"""

from __future__ import annotations

from tools.quality.rulings.__main__ import main
from tools.quality.rulings.derive import INDEX_PATH
from tools.tests.quality.rulings.support import ROUND_14, tree


def test_the_write_arm_creates_the_document(tmp_path, capsys):
    """⭐ The one command a finding's remedy names, run for real."""
    tree(tmp_path, r14=ROUND_14)
    assert main(["--root", str(tmp_path)]) == 0
    written = (tmp_path / INDEX_PATH).read_text(encoding="utf-8")
    assert written.startswith("# The rulings index")
    assert "Ruling 1 — the first thing, settled" in written
    assert "2 rulings" in capsys.readouterr().out


def test_the_check_arm_passes_on_what_the_write_arm_produced(tmp_path, capsys):
    """Exit 0, and the line says how many rulings it derived."""
    tree(tmp_path, r14=ROUND_14)
    main(["--root", str(tmp_path)])
    assert main(["--root", str(tmp_path), "--check"]) == 0
    assert "fresh, 2 rulings" in capsys.readouterr().out


def test_the_check_arm_fails_on_a_stale_document(tmp_path, capsys):
    """⛔ PLANTED: a record added after the write, which is how staleness arrives."""
    tree(tmp_path, r14=ROUND_14)
    main(["--root", str(tmp_path)])
    tree(tmp_path, r15="# CTO — round 15\n\n## ⛔ Ruling 3 — minted later\n")
    assert main(["--root", str(tmp_path), "--check"]) == 1
    assert "STALE" in capsys.readouterr().out


def test_the_check_arm_writes_nothing(tmp_path):
    """A check that repaired its subject could never report on it."""
    tree(tmp_path, r14=ROUND_14)
    assert main(["--root", str(tmp_path), "--check"]) == 1
    assert not (tmp_path / INDEX_PATH).exists()
