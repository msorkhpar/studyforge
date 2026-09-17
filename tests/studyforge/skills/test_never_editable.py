"""`W281`: the adapter and onboarding skills state what `permitted_edits` may never name.

⛔ R19: an integrator learns R3's never-editable targets from the skill, not from a
refusal. Each skill carries ONE statement, and it POINTS at the predicate
(`reads_as_content`) and its vocabulary (`ROOT_DOCUMENTATION`), and at `parse_edits`,
which refuses all three categories. It never restates the names, so the only copy an
integrator reads is `edits.py`'s.

⛔ `W292`: the statement points at FOUR vocabularies, not one — `IGNORE_NAMES`,
`VCS_NAMES` and `VCS_DIRECTORIES` arrive through `parse_edits`. `NEVER_EDITABLE` reads
every one of them from its ONE definition, so each name is on trial here rather than
only root documentation's. ⚠️ **No vocabulary is retyped into this file**: what is
typed is the CATEGORY WORDS, which the statement and the refusal share, and a name is
never one of them.

⭐ What goes RED, each planted: a skill that stops pointing, a pointer that no longer
resolves, a skill that types a name any of the four vocabularies holds, a name a
vocabulary holds that `parse_edits` does not refuse as the category the statement
names, an emptied vocabulary, and a name added to or dropped from the predicate
(through `AUDITED_AGAINST`).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

from studyforge import skills
from studyforge.corpus.manifest import ManifestError, edits, parse_content

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

#: ⛔ `W292`: every vocabulary the statement points at, named by POINTER and never
#: retyped — each row holds the ATTRIBUTE's name, so the population is read out of
#: `edits` when a test runs rather than bound here (`W310/2`: an imported name is a
#: snapshot). Each row also carries the WORDS the statement and `parse_edits`' refusal
#: both use for that category, and the shape of a declaration naming a member: an
#: ignore file and version-control configuration are named as they are, a
#: version-control DIRECTORY is refused at any depth, and a root-documentation stem is
#: declared with a suffix. ⚠️ The words are the category, never a file name.
NEVER_EDITABLE = (
    ("IGNORE_NAMES", "the repository's root ignore file", "{name}"),
    ("VCS_NAMES", "version-control configuration", "{name}"),
    ("VCS_DIRECTORIES", "version-control configuration", "nested/{name}/config"),
    ("ROOT_DOCUMENTATION", "repository-root documentation", "{name}.md"),
)


def _vocabulary(label: str) -> frozenset[str]:
    """Read one never-editable vocabulary from `edits`, its ONE definition."""
    held = getattr(edits, label, None)
    if held is None:
        pytest.fail(f"`edits.{label}` is gone; both statements point at it through parse_edits")
    assert held, f"{label} holds no name, so nothing was checked"
    return held


def _declaring(path: str) -> dict[str, str]:
    """A declaration complete in every other field, so only its target is on trial."""
    return {
        "path": path,
        "kind": "insert-line",
        "anchor": "<modules>",
        "content": "  <module>practice</module>",
        "why": "fabricated, so the only thing this declaration is refused for is its target",
    }


def _types(held: str, text: str, spans: list[str]) -> bool:
    """Whether a skill TYPES this name instead of pointing at the vocabulary holding it.

    ⚠️ A DOTTED name is never an English word, so any occurrence of one is a copy —
    and `git status` in prose is not `.gitignore`, because the dot is required. A bare
    stem IS a word (`W281/1`: the onboarding skill uses the verb *copying*), so it
    counts only in upper case anywhere, or in any case inside a code span.
    """
    if held.startswith("."):
        return re.search(rf"(?i)(?<![\w.]){re.escape(held)}\b", text) is not None
    return bool(re.search(rf"\b{re.escape(held.upper())}\b", text)) or any(
        re.search(rf"(?i)\b{re.escape(held)}\b", span) for span in spans
    )


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
    # ⛔ `W292`: the other three vocabularies reach an integrator ONLY through this
    # pointer, so a statement that stops carrying it stops carrying them.
    assert any(target is edits.parse_edits for target in resolved), pointers


@pytest.mark.parametrize("name", SKILLS)
def test_no_skill_types_a_name_a_never_editable_vocabulary_holds(name):
    # ⭐ Read from every vocabulary, so a name added to one is refused here too. ⚠️ This
    # is `W281`'s `test_no_skill_types_a_name_the_predicate_holds`, widened by `W292`
    # from the predicate's names to all four.
    text, _ = _skill(name)
    spans = re.findall(r"`([^`\n]+)`", text)
    typed = {}
    for label, _, _ in NEVER_EDITABLE:
        held = sorted(one for one in _vocabulary(label) if _types(one, text, spans))
        if held:
            typed[label] = held
    assert typed == {}, f"{name}/SKILL.md types {typed}; point at the vocabulary instead"


@pytest.mark.parametrize(
    ("label", "words", "shape"), NEVER_EDITABLE, ids=[row[0] for row in NEVER_EDITABLE]
)
def test_parse_edits_refuses_every_name_the_statement_points_at(label, words, shape):
    # ⛔ The statement tells an integrator these are refused and to read the names in
    # `edits`. Both halves are on trial: the names come from the vocabulary itself, and
    # each must be refused AS THE CATEGORY the statement names it under.
    unrefused = {}
    for held in sorted(_vocabulary(label)):
        path = shape.format(name=held)
        try:
            edits.parse_edits([_declaring(path)], NOTHING_AT_THE_ROOT)
        except ManifestError as refusal:
            if words not in str(refusal):
                unrefused[path] = str(refusal)
        else:
            unrefused[path] = "accepted"
    assert unrefused == {}, f"{label}: both skills state each of these is refused as {words!r}"


@pytest.mark.parametrize("name", SKILLS)
def test_each_skill_states_every_category_a_declaration_is_refused_by(name):
    # ⛔ A category `parse_edits` refuses and no statement names is a target an
    # integrator meets as a refusal instead of reading in the skill (R19).
    _, statement = _skill(name)
    unstated = sorted({label for label, words, _ in NEVER_EDITABLE if words not in statement})
    assert unstated == [], f"{name}/SKILL.md's statement names no {unstated}"


def test_the_predicate_holds_what_the_statements_were_read_against():
    assert edits.ROOT_DOCUMENTATION == AUDITED_AGAINST, (
        "the predicate's root documentation moved: re-read the never-editable statement "
        f"in {', '.join(SKILLS)}, then move AUDITED_AGAINST"
    )
    for stem in sorted(AUDITED_AGAINST):
        path = f"{stem.upper()}.md"
        assert edits.reads_as_content(path, NOTHING_AT_THE_ROOT) == edits.BY_CONVENTION, path
