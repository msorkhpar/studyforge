r"""The Kotlin guidance in the exercises reference, and the Java guidance it sits beside.

**What it asserts.** The reference's *Kotlin practices* section names every
convention a Kotlin practice needs (test names, the build file, the prime) and
gives each silent pass particular to Kotlin a weak test and a stronger one in a
`kotlin` fence; the shipped skill points to it. ⛔ **The Java guidance did not
move:** the three Java sections under *What the gates cannot see* are held to
the digests they had when the Kotlin section was added, so a changed word there
turns this red.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.authoring.support import fences, section
from tests.support import repository_root

PAGE = repository_root() / "docs" / "authoring" / "exercises.md"
SKILL = repository_root() / "src" / "studyforge" / "skills" / "exercises" / "SKILL.md"
KOTLIN = "Kotlin practices"

#: The Java sections and the sha256 of each, as the reference had them before the Kotlin section.
JAVA_SECTIONS = {
    "Equal, but not the same object": (
        "c5f53d0b0efe2ab735087c755a2f5181e1d60a53c59b8d77526ba8cbea884ad1"
    ),
    "The common silent passes": "fcea791591e75269706dd9dd2eb79c1273db4067ec01137d1ae1e204ca5c2b20",
    "Threads": "0807d866a4f6c08059d3d091e8b59d8ff686f25ce0c4b179460e6df5f5e81aac",
}

#: What each convention's sentence must carry, by the heading it sits under.
CONVENTIONS = {
    "Test names": ("camelCase", "@DisplayName", "parameterised"),
    "The build file": (
        "cleanTest test",
        "exceptionFormat = TestExceptionFormat.FULL",
        "verification-metadata.xml",
        "bootJar",
        'kotlin("reflect")',
        "-XX:+EnableDynamicAgentLoading",
    ),
}

#: The silent passes, each opening its own paragraph in bold.
SILENT_PASSES = (
    "Equality and identity.",
    "Default arguments.",
    "Nullability at the platform boundary.",
    "Time and coroutines under virtual time.",
    "Threads.",
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def page() -> str:
    return PAGE.read_text()


@pytest.mark.parametrize("heading", JAVA_SECTIONS)
def test_a_java_section_has_the_bytes_it_had_before(heading):
    assert digest(section(page(), heading)) == JAVA_SECTIONS[heading]


def test_a_planted_word_in_a_java_section_turns_the_digest_red():
    heading = "The common silent passes"
    planted = section(page(), heading).replace("regex", "pattern", 1)
    assert planted != section(page(), heading), "the plant changed nothing"
    assert digest(planted) != JAVA_SECTIONS[heading]


@pytest.mark.parametrize("heading", CONVENTIONS)
def test_each_convention_is_stated(heading):
    body = section(section(page(), KOTLIN), heading)
    missing = [word for word in CONVENTIONS[heading] if word not in body]
    assert not missing, f"{heading} lacks {missing}"


@pytest.mark.parametrize("name", SILENT_PASSES)
def test_each_silent_pass_is_named_and_the_five_examples_are_kotlin(name):
    body = section(page(), "Silent passes particular to Kotlin")
    assert f"**{name}**" in body
    assert len(fences(body, "kotlin")) >= 4


def test_the_skill_points_at_the_kotlin_section():
    text = SKILL.read_text()
    assert "Silent passes particular to Kotlin" in text
    assert "cleanTest test" in text
    assert "@DisplayName" in text


def test_the_kotlin_section_leaves_java_and_maven_guidance_where_it_was():
    assert page().index("## " + KOTLIN) > page().index("### Threads")
    assert page().index("## " + KOTLIN) < page().index("## Running the pass")
