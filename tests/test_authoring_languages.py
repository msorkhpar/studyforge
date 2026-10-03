"""The languages and the profile the documents name, one line each, are read against the code.

**What it asserts.** `docs/authoring/exercises.md` (*Languages and profiles*) and the root
`README.md` (*What it grades and runs*) each carry one line for Java, Kotlin, Python and TypeScript,
and the profile line names `claude-sdks`; every runtime a language line tells a corpus to declare is
one the manifest accepts; the suffix each language's test has runs under the tool its line names;
and the silent passes particular to Python and TypeScript, and the mock-exam and live-example
guidance, are on the pages the skill sends an author to.

⭐ **The reading can fail.** `missing(text, languages)` is applied to the documents as shipped and
to the same text with one language's line removed, and the second must name that language.

⛔ Nothing under `src/` names a profile, so the profile line is a documentation line only.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.manifest.runtimes import RUNTIMES
from studyforge.execute.testargv import argv_for
from tests.authoring.support import document, rows_under, section
from tests.support import repository_root

LANGUAGES = ("Java", "Kotlin", "Python", "TypeScript")
PROFILE = "claude-sdks"
HEADING = "Languages and profiles"
README_HEADING = "What it grades and runs"

#: What each language's documented line must say about how it is run, read against the code.
TESTS = {"Python": "test_x.py", "TypeScript": "x.test.ts"}


def missing(text: str, languages=LANGUAGES) -> list[str]:
    """The languages `text` has no line for, in the order asked."""
    return [name for name in languages if not re.search(rf"(?m)^(\| |- \*\*){name}\b", text)]


def readme() -> str:
    return (repository_root() / "README.md").read_text(encoding="utf-8")


def exercises_section() -> str:
    return "## " + HEADING + "\n" + section(document("exercises.md"), HEADING)


def readme_section() -> str:
    text = readme()
    start = text.index(f"## {README_HEADING}")
    return text[start : text.index("\n## ", start + 3)]


def test_the_exercises_page_and_the_readme_each_have_a_line_for_every_language():
    assert missing(exercises_section()) == []
    assert missing(readme_section()) == []


@pytest.mark.parametrize("language", LANGUAGES)
def test_a_removed_line_is_named_by_the_reading(language):
    for text in (exercises_section(), readme_section()):
        kept = "\n".join(
            line
            for line in text.splitlines()
            if not re.match(rf"(\| |- \*\*){language}\b", line)
        )
        assert missing(kept) == [language]


def test_the_profile_line_names_the_profile_and_each_language_it_serves():
    for text in (exercises_section(), readme_section()):
        assert PROFILE in text
    assert "Claude SDKs" in exercises_section()
    assert "all four languages" in exercises_section().split("**Profiles.**")[1]


def test_every_runtime_a_language_line_declares_is_one_the_manifest_accepts():
    rows = rows_under(exercises_section(), HEADING)
    declared = {name for row in rows for name in re.findall(r"`([a-z]+)`", row[-1])}
    assert declared == {"java", "maven", "gradle", "kotlin", "python", "node"}
    assert declared <= set(RUNTIMES)


def test_each_language_s_test_suffix_runs_under_the_tool_its_line_names():
    python = argv_for({}, "tests/test_x.py", "", ["python"])
    node = argv_for({}, "tests/x.test.ts", "", ["node"])
    assert python is not None and "pytest" in python
    assert node is not None and node[:2] == ["node", "--test"]
    rows = {row[0]: row for row in rows_under(exercises_section(), HEADING)}
    assert "pytest" in rows["Python"][1]
    assert "node --test" in rows["TypeScript"][1]


@pytest.mark.parametrize(
    "phrase",
    [
        "A test that asserts nothing",
        "Truthiness",
        "A tuple asserted",
        "Identity against equality",
        "A mutable default argument",
        "A missing `await`",
        "Loose equality",
        "An `any` that hides a type error",
        "`enum`, parameter properties and `namespace` under type stripping",
        "A stub that returns without asserting",
    ],
)
def test_each_silent_pass_particular_to_python_and_typescript_is_written_down(phrase):
    text = section(document("exercises.md"), "Python and TypeScript silent passes")
    assert phrase in text


def test_the_mock_exam_and_the_live_example_guidance_are_where_the_skill_sends_the_author():
    exercises = document("exercises.md")
    assert "**Authoring one.**" in section(exercises, "A mock exam")
    for gate in ("`P1`", "`Q1`", "`Q2`", "`Q3`"):
        assert gate in section(exercises, "A mock exam")
    corpus = document("corpus.md")
    assert "What a live-capable example may and may not contain" in corpus
    skill = (
        repository_root() / "src" / "studyforge" / "skills" / "exercises" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "A mock exam is a quiz",
        "A live-capable example holds no key",
        "silent passes of its own",
    ):
        assert phrase in skill
