"""`W281`: the adapter and onboarding skills state what `permitted_edits` may never name.

⛔ R19: an integrator learns R3's never-editable targets from the skill, not from a
refusal. Each skill carries ONE statement, and it POINTS at the predicate
(`reads_as_content`) and its vocabulary (`ROOT_DOCUMENTATION`). It never restates the
names, so the only copy an integrator reads is `edits.py`'s.

⭐ What goes RED, each planted: a skill that stops pointing, a pointer that no longer
resolves, a skill that types a root-documentation name, and a name added to or dropped
from the predicate (through `AUDITED_AGAINST`).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

from studyforge import skills
from studyforge.corpus.manifest import edits, parse_content

#: The skills that tell an integrator what `permitted_edits` may name.
SKILLS = ("adapter", "onboarding")

#: The words that open each skill's one never-editable statement.
STATEMENT = "`permitted_edits` may never name"

#: ⛔ The vocabulary both statements were last read against. No skill carries it. A
#: name added to or dropped from the predicate goes RED here, and the repair is to
#: re-read both statements, whose words describe the category rather than list its
#: members, and then move this pin.
AUDITED_AGAINST = frozenset({"readme", "license", "licence", "copying"})

#: A policy that includes no root file, so only the convention reads one as content.
NOTHING_AT_THE_ROOT = parse_content({"include": ["src/*.md"], "exclude": []})


def _skill(name: str) -> tuple[str, str]:
    """Return the skill's text and its one never-editable statement."""
    text = (Path(skills.__file__).parent / name / "SKILL.md").read_text("utf-8")
    # ⚠️ A paragraph, or one bullet of a list: a statement is never read with its neighbours.
    blocks = [block for block in re.split(r"\n\s*\n|\n(?=- )", text) if STATEMENT in block]
    assert len(blocks) == 1, f"{name}/SKILL.md carries {len(blocks)} statements; it owes one"
    return text, " ".join(blocks[0].split())


def _resolve(dotted: str) -> object:
    """Import the longest module prefix of `dotted` and read the rest as attributes."""
    parts = dotted.split(".")
    for cut in range(len(parts), 0, -1):
        try:
            target: object = importlib.import_module(".".join(parts[:cut]))
        except ModuleNotFoundError:
            continue
        for attribute in parts[cut:]:
            if not hasattr(target, attribute):
                pytest.fail(f"the pointer `{dotted}` does not resolve at {attribute!r}")
            target = getattr(target, attribute)
        return target
    pytest.fail(f"the pointer `{dotted}` names no module")


@pytest.mark.parametrize("name", SKILLS)
def test_each_skill_points_at_the_predicate_and_its_vocabulary(name):
    _, statement = _skill(name)
    pointers = re.findall(r"`(studyforge(?:\.\w+)+)`", statement)
    resolved = [_resolve(pointer) for pointer in pointers]
    assert "repository-root documentation" in statement
    assert any(target is edits.reads_as_content for target in resolved), pointers
    assert any(target is edits.ROOT_DOCUMENTATION for target in resolved), pointers


@pytest.mark.parametrize("name", SKILLS)
def test_no_skill_types_a_name_the_predicate_holds(name):
    # ⭐ Read from the predicate, so a name added there is refused here too. A name is
    # typed when it is upper case anywhere, or in any case inside a code span; the
    # lower-case verb *copying* in prose is not a file name.
    text, _ = _skill(name)
    assert edits.ROOT_DOCUMENTATION, "the predicate holds no name, so nothing was checked"
    spans = re.findall(r"`([^`\n]+)`", text)
    typed = sorted(
        stem
        for stem in edits.ROOT_DOCUMENTATION
        if re.search(rf"\b{re.escape(stem.upper())}\b", text)
        or any(re.search(rf"(?i)\b{re.escape(stem)}\b", span) for span in spans)
    )
    assert typed == [], f"{name}/SKILL.md types {typed}; point at ROOT_DOCUMENTATION instead"


def test_the_predicate_holds_what_the_statements_were_read_against():
    assert edits.ROOT_DOCUMENTATION == AUDITED_AGAINST, (
        "the predicate's root documentation moved: re-read the never-editable statement "
        f"in {', '.join(SKILLS)}, then move AUDITED_AGAINST"
    )
    for stem in sorted(AUDITED_AGAINST):
        path = f"{stem.upper()}.md"
        assert edits.reads_as_content(path, NOTHING_AT_THE_ROOT) == edits.BY_CONVENTION, path
