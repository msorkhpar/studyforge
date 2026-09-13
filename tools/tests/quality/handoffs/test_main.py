"""Mirror of `tools/quality/handoffs/__main__.py` (R12).

⛔ **The exit code is the deliverable**, so each code is asserted from a tree
that earns it, and the command is run once as a real subprocess: the reason the
command lives in `__main__` is a warning only a real `python3 -m` can print.
"""

from __future__ import annotations

import sys

from tests.support import repository_root, run
from tools.quality.handoffs import HANDOFF_DIR
from tools.quality.handoffs.__main__ import main
from tools.quality.handoffs.contract import FINDING_MARKERS, MARKER_STRUCTURAL
from tools.quality.handoffs.sweep import CONVENTIONS_DIR, FINDING_LINE, IN_TEXT

MARK = MARKER_STRUCTURAL
ESCAPED = "\\[" + MARK.strip("`[]") + "\\]"


def write(root, relative, text):
    """Put `text` at `relative` under a temporary tree."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_the_command_prints_every_line_with_its_document(tmp_path, capsys):
    write(tmp_path, f"{HANDOFF_DIR}/W99.md", f"- W99/1 {MARK} a\nsaid {MARK} b\n")
    assert main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("marker sweep: ") and "1 documents read" in out[0]
    assert out[1:] == [
        f"{HANDOFF_DIR}/W99.md:1: {FINDING_LINE}: - W99/1 {MARK} a",
        f"{HANDOFF_DIR}/W99.md:2: {IN_TEXT}: said {MARK} b",
    ]


def test_an_empty_population_moves_the_exit_code(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 2
    assert "EMPTY population" in capsys.readouterr().out


def test_a_weak_pattern_moves_the_exit_code(tmp_path, capsys):
    write(tmp_path, f"{CONVENTIONS_DIR}/flow.md", f"grep -rn '{ESCAPED}' docs/\n")
    assert main(["--root", str(tmp_path), "--patterns"]) == 1
    assert ": weak: " in capsys.readouterr().out
    write(tmp_path, f"{CONVENTIONS_DIR}/flow.md", f"grep -rn '`{ESCAPED}`' docs/\n")
    assert main(["--root", str(tmp_path), "--patterns"]) == 0


def test_the_vocabulary_is_the_shipped_constant(capsys):
    assert main(["--vocabulary"]) == 0
    assert tuple(capsys.readouterr().out.splitlines()) == FINDING_MARKERS


def test_the_real_command_runs_clean_on_the_shipped_tree():
    root = repository_root()
    result = run([sys.executable, "-m", "tools.quality.handoffs"], cwd=root)
    assert result.returncode == 0, result.stderr
    assert "RuntimeWarning" not in result.stderr
    assert result.stdout.startswith("marker sweep: ")
