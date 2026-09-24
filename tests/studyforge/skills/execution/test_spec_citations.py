"""Every refusal the execution skill raises cites the spec as the spec is numbered (`W462/1`).

⚠️ **Measured:** `rulings` and `onboard` said "§8.1 ruling 1"–"4" in their
refusals, and §8.1 numbers no rulings: it states them as the bullets of *"what
the compose side gets right"*. A reader who looked for "ruling 2" found nothing.
⭐ So this reads every string the package can put in a message — each constant,
and each literal part of an f-string, but no docstring — and holds two rules:
no string says "ruling <number>", and every "§<number>" is a section heading the
spec carries.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import studyforge.skills.execution as package
from studyforge.skills.execution import onboard, rulings
from tests.studyforge.skills.execution.contracts import editor_contract

ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "docs" / "specs" / "2026-09-08-studyforge-v1-design.md"
MODULES = sorted(Path(package.__file__).parent.glob("*.py"))

#: A numbered ruling, which the spec does not have.
NUMBERED_RULING = re.compile(r"\bruling \d", re.IGNORECASE)
#: A section citation.
SECTION = re.compile(r"§(\d+(?:\.\d+)*)")


def sections() -> set[str]:
    """Every section number the spec's own headings carry (`## 8.`, `### 8.1`)."""
    found = re.findall(r"^#{2,3} (\d+(?:\.\d+)*)\.?\s", SPEC.read_text(encoding="utf-8"), re.M)
    return set(found)


def messages(path: Path) -> list[str]:
    """Every string constant in one module that is not a docstring."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def test_the_spec_is_read_and_carries_the_sections_the_package_cites():
    assert {"8.1", "8.3", "11.0"} <= sections()


@pytest.mark.parametrize("path", MODULES, ids=lambda path: path.name)
def test_no_message_cites_a_numbered_ruling(path: Path):
    assert [one for one in messages(path) if NUMBERED_RULING.search(one)] == []


@pytest.mark.parametrize("path", MODULES, ids=lambda path: path.name)
def test_every_section_a_message_cites_is_a_heading_of_the_spec(path: Path):
    cited = {number for one in messages(path) for number in SECTION.findall(one)}
    assert cited - sections() == set()


def test_every_compose_refusal_names_its_rule_in_words():
    """A block breaking all four §8.1 rules at once, and each refusal read as raised."""
    block = editor_contract()["editor"]
    block["ports"][0]["host_bind"] = "0.0.0.0"
    block["mounts"][0]["host_path"] = "~"
    block["mounts"][0]["must_exist_before_start"] = False
    block["runs_as"] = {}
    found = rulings.findings(block, name="editor")
    assert len(found) >= 4
    for one in found:
        assert not NUMBERED_RULING.search(one), one
        assert "§8.1" in one or "§8.3" in one


def test_the_source_root_refusals_name_the_rule_in_words():
    from tests.studyforge.skills.execution.test_onboard import manifest

    for include in (["*.md"], ["a/*.md", "b/*.md"]):
        with pytest.raises(onboard.ExecutionRefused) as refused:
            onboard.source_root(manifest(content={"include": include, "exclude": []}))
        assert not NUMBERED_RULING.search(str(refused.value))
        assert "§8.1" in str(refused.value) and "only the sources" in str(refused.value)
