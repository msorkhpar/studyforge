"""Mirror of `tests/floor/__main__.py`: the exit code, and one plant per product rule.

⭐ **The exit code is the deliverable**, so each rule is planted in a scratch tree and the
product's own command — `python3 -m tests.floor`, run as a real subprocess — is asserted to
refuse it by name. ⛔ A clean scratch tree exits zero first, so a refusal below is the plant's
and never the tree's.

⛔ **The personal-data plant is ASSEMBLED at run time** from fragments, so this file never holds
the shape it plants; the account name in it is a fabricated placeholder.
"""

from __future__ import annotations

import sys

import pytest

from tests.floor.__main__ import SCOPE, main
from tests.support import repository_root, run

#: A module docstring that satisfies R17, for every planted module that is not the R17 plant.
CONTRACT = '"""A planted module: what it does, how you use it, and what it depends on."""\n'


def write(root, relative, text):
    """Write `text` at `root/relative`, creating its directories."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def clean_tree(root):
    """A scratch tree on the floor: one framework module, its contract and its mirrored test."""
    write(root, "src/studyforge/planted.py", CONTRACT + "\nVALUE = 1\n")
    write(root, "tests/studyforge/test_planted.py", "def test_it():\n    assert True\n")
    return root


def floor(root):
    """Run the product floor over `root` through the command a stranger types."""
    return run([sys.executable, "-m", "tests.floor", "--root", str(root)], cwd=repository_root())


def test_a_clean_tree_exits_zero_and_says_so_last(tmp_path, capsys):
    assert main(["--root", str(clean_tree(tmp_path))]) == 0
    printed = capsys.readouterr().out.strip().splitlines()
    assert printed[-2] == "quality floor: clean"
    assert printed[-1] == SCOPE


def test_the_command_exits_zero_on_a_clean_tree(tmp_path):
    result = floor(clean_tree(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def _oversized(root):
    body = "".join(f"VALUE_{number} = {number}\n" for number in range(400))
    write(root, "src/studyforge/planted.py", CONTRACT + body)


def _personal_data(root):
    # ⛔ Assembled, never written whole: a home path under a fabricated account name.
    write(root, "docs/notes.md", "kept at /" + "home/" + "jane-placeholder" + "/notes\n")


def _unmirrored(root):
    write(root, "src/studyforge/lonely.py", CONTRACT)


def _no_contract(root):
    write(root, "src/studyforge/planted.py", "VALUE = 1\n")


def _framework_names_a_source(root):
    write(root, "src/studyforge/planted.py", CONTRACT + "# ported from " + "SPARQL" + " notes\n")


#: `(rule, the plant, the tag the refusal carries)` — one per product rule.
PLANTS = [
    pytest.param("R11", _oversized, "[size]", id="R11-size"),
    pytest.param("R7", _personal_data, "[personal-data]", id="R7-personal-data"),
    pytest.param("R12", _unmirrored, "[mirror]", id="R12-mirror"),
    pytest.param("R17", _no_contract, "[contract]", id="R17-contract"),
    pytest.param("R1", _framework_names_a_source, "[source-name]", id="R1-source-name"),
]


@pytest.mark.parametrize(("rule", "plant", "tag"), PLANTS)
def test_each_rule_planted_is_refused_by_the_products_own_command(tmp_path, rule, plant, tag):
    root = clean_tree(tmp_path)
    plant(root)
    result = floor(root)
    assert result.returncode == 1, f"{rule} was not refused:\n{result.stdout}{result.stderr}"
    findings = [line for line in result.stdout.splitlines() if "] " in line and ": [" in line]
    assert findings, result.stdout
    assert all(tag in line for line in findings), findings
    assert result.stdout.strip().splitlines()[-2] == "quality floor: 1 finding"


def test_a_finding_never_carries_the_value_it_found(tmp_path):
    root = clean_tree(tmp_path)
    _personal_data(root)
    result = floor(root)
    assert "jane-placeholder" not in result.stdout + result.stderr
