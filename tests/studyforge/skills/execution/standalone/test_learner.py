"""Mirror of `src/studyforge/skills/execution/standalone/learner.py` (R12)."""

from __future__ import annotations

import os
import re

import pytest

from studyforge.skills.execution.standalone import compose, images, learner, pages, tour
from studyforge.skills.execution.standalone.facts import Facts

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
        f"{images.NAMESPACE_VARIABLE}=",
    ):
        assert line in text.splitlines(), line


def test_the_readme_names_the_exercises_and_how_they_relate_to_the_practices():
    with_them = learner.readme(learner.Course("A Course", "a-course", 1, 2, "ns", False, True))
    assert "`exercises/`" in with_them and "`practice/`" in with_them
    assert build_words(with_them) == []
    assert "exercises/" not in learner.readme(COURSE)


def names_variable_in_the_copy_step(text: str) -> bool:
    """Whether the step that copies `course.env` also names the account variable."""
    lines = text.splitlines()
    step = next(i for i, line in enumerate(lines) if line.startswith("3. Copy `course.env`"))
    return images.NAMESPACE_VARIABLE in " ".join(lines[step : step + 2])


def test_the_readme_steps_a_friend_through_the_pull_and_names_the_account_variable():
    text = learner.readme(COURSE)
    assert names_variable_in_the_copy_step(text)
    assert "cp course.env .env" in text
    assert "docker compose -f compose.pull.yaml up -d" in text
    assert "amd64" in text and "Apple Silicon" in text and "emulation" in text
    assert "docker compose -f compose.pull.yaml ps" in text
    assert "docker compose -f compose.pull.yaml down" in text
    assert text.index("cp course.env .env") < text.index("compose.pull.yaml up -d")


def test_a_readme_that_did_not_name_the_account_variable_would_be_caught():
    planted = learner.readme(COURSE).replace(
        f"set `{images.NAMESPACE_VARIABLE}` in it", "set the account in it"
    )
    assert not names_variable_in_the_copy_step(planted)


def test_the_settings_leave_the_account_empty_and_show_only_a_placeholder():
    text = learner.settings(COURSE)
    assert f"{images.NAMESPACE_VARIABLE}=" in text.splitlines()
    assert f"# {images.NAMESPACE_VARIABLE}={learner.NAMESPACE_PLACEHOLDER}" in text.splitlines()
    assert learner.NAMESPACE_PLACEHOLDER == "your-dockerhub-account"


BIG = Facts(
    modules=45,
    units=166,
    practices=906,
    quizzes=163,
    examples=182,
    areas=("Java Fundamentals", "Exception Handling"),
)
SMALL = Facts(modules=3, units=38, practices=45, quizzes=2)
SHOTS = tuple((role, f".studyforge/images/readme/{role}.webp") for role, _ in tour.ROLES)


def rich(facts: Facts, shots=(), narrated=True) -> str:
    return learner.readme(
        learner.Course(
            "A Course",
            "a-course",
            18772,
            18444,
            "ns",
            narrated,
            True,
            facts,
            shots,
            ("java", "maven"),
            True,
        )
    )


def headings(text: str) -> list[str]:
    return [line[3:] for line in text.splitlines() if line.startswith("## ")]


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")


def test_the_readme_states_each_course_s_own_numbers_and_only_those():
    big, small = rich(BIG), rich(SMALL)
    assert (
        "166 units in 45 modules, grouped in 2 topic areas: Java Fundamentals and Exception" in big
    )
    assert "906 practices: 743 to write in code" in big and "163 short quizzes" in big
    assert "3 modules and 38 units" in small
    assert "45 practices: 43 to write in code" in small and "2 short quizzes" in small
    assert "topic area" not in small and "166" not in small and "906" not in small
    assert "38 units" not in big and "45 practices" not in big


def test_a_number_that_was_not_read_is_not_printed_and_its_feature_is_not_described():
    bare = rich(Facts(units=10))
    assert "It has 10 units." in bare
    assert "practices:" not in bare and "modules" not in bare
    for feature in ("Practices graded", "Quizzes graded", "Code examples", "workspace"):
        assert feature not in bare, feature
    assert "Quizzes, graded in the page" not in bare and "Run and Submit" not in bare
    assert "Lessons." in bare and "Reading marks" in bare


def test_the_readme_names_every_feature_the_course_has_and_the_comparison_shows_them():
    text = rich(BIG)
    for phrase in (
        "Practices graded by a real runner",
        "The practice workspace",
        "resize the panes",
        "worked solution",
        "**Run**",
        "**Submit**",
        "Quizzes graded in the page",
        "Code examples that open in an editor",
        "Reading marks and progress",
        "Optional narration",
    ):
        assert phrase in text, phrase
    table = [line for line in text.splitlines() if line.startswith("| ") and "Read-only" in line]
    assert table == ["| | Read-only preview | Full course, with Docker |"]
    rows = text.split("| | Read-only preview | Full course, with Docker |")[1].split("\n\n")[0]
    assert rows.count("\n| ") >= 8
    assert "Code examples opened in the editor" not in rich(SMALL)


def test_the_readme_has_the_section_every_preview_note_points_to():
    text = rich(BIG)
    assert headings(text).count(tour.RUN_HEADING) == 1
    assert slug(tour.RUN_HEADING) == tour.RUN_ANCHOR
    assert f"(#{tour.RUN_ANCHOR})" in text


def test_every_link_inside_the_readme_reaches_a_heading_of_it():
    text = rich(BIG, SHOTS)
    anchors = {slug(one) for one in headings(text)}
    for target in re.findall(r"\]\(#([^)]+)\)", text):
        assert target in anchors, target


def test_the_readme_points_to_the_preview_without_a_url_and_names_no_account():
    text = rich(BIG, SHOTS)
    assert "website link at the top of this repository" in text
    assert "github.io" not in text and "github.com" not in text
    assert "https://" not in text


#: The environment variable that names the accounts a README must never carry, as a
#: comma-separated list. The values are never written in source.
PRIVATE_NAMES = "STUDYFORGE_PRIVATE_NAMES"


def names_in(text: str, names: list[str]) -> list[str]:
    """Which of `names` the text carries, in any case."""
    lowered = text.lower()
    return [name for name in names if name and name.lower() in lowered]


def test_the_readme_names_no_account_the_environment_lists():
    names = [one.strip() for one in os.environ.get(PRIVATE_NAMES, "").split(",")]
    if not any(names):
        pytest.skip(f"{PRIVATE_NAMES} is unset, so there is no private name to look for")
    assert names_in(rich(BIG, SHOTS), names) == []


def test_a_planted_account_name_is_found_in_the_readme_and_a_clean_one_is_not():
    placeholder = ["janedoe"]
    clean = rich(BIG, SHOTS)
    assert names_in(clean, placeholder) == []
    assert names_in(clean + "\nMaintained by JaneDoe.\n", placeholder) == placeholder


def test_the_readme_keeps_the_windows_commands_beside_the_unix_ones():
    text = rich(BIG)
    assert "cp course.env .env" in text and "copy course.env .env" in text
    assert f"sh {learner.RESTORE_SH}" in text and f"pwsh {learner.RESTORE_PS1}" in text


def test_the_pictures_are_shown_in_the_order_of_their_roles_and_only_when_given():
    text = rich(BIG, SHOTS)
    images_in = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", text)
    assert images_in == [path for _, path in SHOTS]
    assert "![" not in rich(BIG)
    assert len(re.findall(r"!\[", rich(BIG, SHOTS[:2]))) == 2


def test_the_full_readme_still_says_nothing_about_the_build_but_one_line_to_its_branch():
    text = rich(BIG, SHOTS)
    assert build_words(text) == []
    assert sum(learner.BUILD_BRANCH in line for line in text.splitlines()) == 1


def test_a_readme_that_lost_its_run_section_would_be_caught():
    planted = rich(BIG).replace(f"## {tour.RUN_HEADING}", "## Start it")
    assert headings(planted).count(tour.RUN_HEADING) == 0
    anchors = {slug(one) for one in headings(planted)}
    assert any(target not in anchors for target in re.findall(r"\]\(#([^)]+)\)", planted))


def test_the_licence_is_linked_only_when_the_tree_holds_it():
    assert "[`LICENSE`](LICENSE)" in rich(BIG)
    unlicensed = learner.readme(learner.Course("A", "a", 1, 2, "ns", False))
    assert "[`LICENSE`]" not in unlicensed and "`LICENSE`" in unlicensed


def test_the_readme_says_how_the_online_preview_is_kept_and_switched_on():
    text = learner.readme(COURSE)
    assert headings(text).count("The online preview") == 1
    assert "built automatically from `main` on every push" in text
    assert '"GitHub Actions" as the source' in text and "open Settings, then Pages" in text
    assert f"(`{pages.WORKFLOW}`)" not in text and f"({pages.WORKFLOW})" in text
    assert "website link at the top of this repository" in text
    assert "gh-pages" not in text and "https://" not in text and "github.io" not in text
