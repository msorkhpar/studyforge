"""Mirror of `src/studyforge/skills/execution/standalone/learner.py` (R12)."""

from __future__ import annotations

import re

from studyforge.skills.execution.standalone import compose, images, learner

COURSE = learner.Course(
    title="A Course",
    project="a-course",
    site_port=18772,
    editor_port=18444,
    namespace=images.NAMESPACE_DEFAULT,
    narrated=True,
)

#: Words a learner's README never needs: how the course was built.
BUILD_WORDS = re.compile(r"(?i)\b(ingest\w*|adapter|archive|skills?|onboard\w*|studyforge build)\b")


def build_words(text: str) -> list[str]:
    """Every build word in `text` outside the one line that points to the build branch."""
    return [
        word
        for line in text.splitlines()
        if learner.BUILD_BRANCH not in line
        for word in BUILD_WORDS.findall(line)
    ]


def test_the_readme_says_what_it_needs_how_to_start_and_where_it_listens():
    text = learner.readme(COURSE)
    assert text.startswith("# A Course\n")
    assert "docker compose up -d --build" in text
    assert "docker compose -f compose.pull.yaml up -d" in text
    assert "http://127.0.0.1:18772/" in text
    assert "http://127.0.0.1:18444/" in text
    assert "Docker" in text and "no Java, no Python" in text


def test_the_readme_says_how_to_get_narration_and_that_the_site_works_without_it():
    text = learner.readme(COURSE)
    assert learner.RESTORE_SH in text and learner.RESTORE_PS1 in text
    assert "complete without narration" in text
    assert f"{images.NARRATION_VARIABLE}={images.NARRATIONS[1]}" in text
    silent = learner.readme(learner.Course("A Course", "a-course", 1, 2, "ns", False))
    assert learner.RESTORE_SH not in silent


def test_the_readme_says_nothing_about_the_build_but_one_line_to_its_branch():
    text = learner.readme(COURSE)
    assert build_words(text) == []
    assert sum(learner.BUILD_BRANCH in line for line in text.splitlines()) == 1


def test_a_readme_that_explained_ingestion_would_be_caught():
    planted = learner.readme(COURSE) + "\nThe pages were made by ingesting the archive.\n"
    assert build_words(planted)


def test_the_settings_name_every_variable_the_compose_files_read_at_its_default():
    text = learner.settings(COURSE)
    for line in (
        f"{compose.SITE_PORT_VARIABLE}=18772",
        f"{compose.EDITOR_PORT_VARIABLE}=18444",
        f"{images.NARRATION_VARIABLE}={images.NARRATIONS[0]}",
        f"{compose.PROJECT_VARIABLE}=a-course",
        f"{images.NAMESPACE_VARIABLE}={images.NAMESPACE_DEFAULT}",
    ):
        assert line in text.splitlines(), line


def test_the_readme_names_the_exercises_and_how_they_relate_to_the_practices():
    with_them = learner.readme(learner.Course("A Course", "a-course", 1, 2, "ns", False, True))
    assert "`exercises/`" in with_them and "`practice/`" in with_them
    assert build_words(with_them) == []
    assert "exercises/" not in learner.readme(COURSE)
