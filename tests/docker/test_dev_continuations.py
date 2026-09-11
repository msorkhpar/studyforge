"""Every reader of `docker/dev/` text, classified — and the claim is CLOSED (`W131`).

⛔ **The defect this module exists to make unrepeatable.** Four shipped checks in
this directory certified properties of `docker/dev/Dockerfile` that they could not
observe, because they split the file into PHYSICAL lines and every package this
Dockerfile installs sits on a backslash CONTINUATION below the line that names the
installer. ⭐ All four were confirmed by PLANT rather than by reading — the live
reading was green and stayed green with the forbidden word planted — and rounds 36
onward quoted that green (`docs/tasks/handoffs/W131.md`, Ruling 267):

```text
test_the_browser_does_not_arrive_from_a_package_manager    bare `chromium`  -> PASSED
test_the_runtime_arrives_pinned_rather_than_from_a_package_manager `nodejs` -> PASSED
test_the_archive_comes_from_an_immutable_per_version_url   `/latest/`       -> PASSED
test_studyforge_is_not_installed_into_the_image            a 2nd install    -> PASSED
```

⚠️ **Why a registry and not just five fixed checks.** The remedy for those four is
`commands()`, and it is copyable — which is exactly the problem: the NEXT reader of
this Dockerfile will reach for `.splitlines()` because it is shorter, and their
check will be green on the day it ships. ⛔ So the population of readers is asserted
here, CLOSED in both directions (Ruling 258): a site that appears and is not
classified fails, and a classification whose site has gone fails too. ⭐ An
incomplete list of safe sites is worse than no list, because it reads as a sweep.

⛔ **And the `line-anchored` verdict is not taken on trust.** *"A continuation
cannot carry `FROM `"* is a claim about the TOKEN SET (Ruling 220), so it is
ASSERTED against the real files rather than reasoned about: every continuation line
in `docker/dev/` is read, and none of them may begin with any declared anchor.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV, commands, read
from tests.support import repository_root

#: The readers whose result is one LOGICAL line or one COMMAND rather than one
#: physical line. ⛔ A site is `collapsed` only if it goes through one of these or
#: performs the collapse itself, and that is checked rather than declared.
COLLAPSING_READERS = ("commands", "joined")

#: The literal collapse, for the one site that performs it rather than calling it.
COLLAPSE = 'replace("\\\\\\n", " ")'

#: ⛔ **EVERY SITE IN `tests/docker/` THAT DECOMPOSES `docker/dev/` TEXT, BY THE
#: FUNCTION THAT OWNS IT.** Closed claim — see this module's docstring.
#:
#: `collapsed`         continuations are joined before the split, so one element is
#:                     one logical line or one shell command.
#: `line-anchored`     the predicate matches only at the START of a line and selects
#:                     a construct the file's grammar puts only at the start of a
#:                     LOGICAL line (a Dockerfile instruction keyword, a `set --`
#:                     command, a YAML sequence entry). A real instance therefore
#:                     cannot ride a continuation — ASSERTED below, not assumed —
#:                     and a coincidental match only ADDS a member, which every one
#:                     of these sites turns into a failing exact count.
#: `comment-filter`    removes comment lines rather than selecting anything. Its
#:                     risk is a SPLICE, not a miss, and that is asserted below.
#: `no-continuations`   the file it reads has NO continuation lines at all, so a
#:                     physical line IS a logical line there. ⚠️ That is a fact about
#:                     the artefact rather than about the predicate, so it is the one
#:                     verdict that can stop being true without anybody touching a
#:                     test — which is why it is asserted rather than assumed.
#: `per-physical-line` reads continuation lines DELIBERATELY, because that is where
#:                     its subject lives; completeness guarded by an exact count.
#: `not-dev-text`      does not read `docker/dev/` text at all.
#:
#: ⚠️ Where more than one verdict is true of a site, the one recorded is the GROUND
#: the exemption rests on. `requirement_names` filters comments AND reads a file with
#: no continuations; it is recorded as `no-continuations` because that is the claim
#: an assertion below can falsify.
CLASSIFIED_BY_MODULE: dict[str, dict[str, str]] = {
    "devfiles.py": {
        "instructions": "comment-filter",
        "commands": "collapsed",
    },
    "test_dev_check_timeout.py": {
        "check_line": "collapsed",
        "test_the_bound_runs_inside_the_container_and_not_on_the_host": "collapsed",
        "test_the_no_argument_case_names_the_image_s_own_command": "line-anchored",
    },
    "test_dev_image.py": {
        "requirement_names": "no-continuations",
        "test_every_tool_version_is_pinned_exactly": "no-continuations",
        "test_studyforge_is_not_installed_into_the_image": "collapsed",
        "test_the_base_image_is_pinned_by_digest": "line-anchored",
        "test_the_base_image_is_python_314": "line-anchored",
        "test_the_runtime_arrives_pinned_rather_than_from_a_package_manager": "collapsed",
        "test_the_runtime_is_verified_against_a_recorded_checksum": "line-anchored",
        "test_the_source_is_mounted_not_copied": "line-anchored",
        "test_the_suite_passes_inside_the_image_with_no_network": "not-dev-text",
    },
    "test_dev_image_browser.py": {
        "recorded_digests": "per-physical-line",
        "test_an_architecture_with_no_recorded_checksum_fails_loudly": "collapsed",
        "test_the_archive_comes_from_an_immutable_per_version_url": "collapsed",
        "test_the_browser_does_not_arrive_from_a_package_manager": "collapsed",
        "test_the_browser_is_verified_against_a_recorded_checksum": "line-anchored",
        "test_the_font_does_not_arrive_unconstrained": "collapsed",
        "test_the_visual_harness_variables_cross_into_the_container": "no-continuations",
    },
    # ⭐ And this module is inside its own population, which is the point: an
    # instrument exempt from the rule it enforces is the defect one level up.
    "test_dev_continuations.py": {
        "continuation_lines": "per-physical-line",
        "test_commands_joins_text_that_raw_lines_keep_apart": "collapsed",
        "test_the_two_control_packages_are_still_on_different_lines": "per-physical-line",
    },
}

#: The same thing keyed the way a site is named, `module::function`. ⚠️ Nested above
#: only so that no key runs past the line limit; this is the form every assertion
#: below reads.
CLASSIFIED: dict[str, str] = {
    f"{module}::{function}": verdict
    for module, functions in CLASSIFIED_BY_MODULE.items()
    for function, verdict in functions.items()
}

#: Decomposition sites, the unit being SOURCE LINES rather than functions — two
#: functions own two each. ⛔ Declared separately from `CLASSIFIED` on purpose: a
#: second site added inside an ALREADY-classified function would otherwise enter
#: the suite unexamined, which is the shape of every defect this module is about.
DECOMPOSITION_SITES = 25

#: ⛔ **THE ANCHORS THE `line-anchored` VERDICT RESTS ON, per file.** Each is a
#: prefix some site above matches against the start of a (stripped) line. ⚠️ `#` is
#: deliberately absent: a comment is not SELECTED by any site, it is removed, and
#: the risk there is a splice rather than a miss — `test_no_comment_sits_inside_a
#: _continued_instruction` is that half.
#:
#: ⛔ Only the two files that HAVE continuations appear, so neither reading below is
#: a vacuous pass (Ruling 191). `compose.yaml` and `requirements.txt` have none at
#: all and `test_the_files_with_no_continuations_still_have_none` is their ground.
LINE_ANCHORS: dict[str, tuple[str, ...]] = {
    "Dockerfile": ("FROM ", "COPY ", "CMD ", "ARG "),
    "check": ("set --",),
}

#: The files a `no-continuations` site may read, and the claim that names them.
CONTINUATION_FREE = ("compose.yaml", "requirements.txt")

#: ⭐ MEASURED at `51dee3b` in the pinned image, the unit being PHYSICAL LINES that
#: continue the line above them: **89** in `Dockerfile`, **2** in `check`, **0** in
#: `compose.yaml` and **0** in `requirements.txt`. ⛔ The bound
#: is a floor and not the figure, because a package added to the browser's list
#: moves the number and does not move the property — but a reading of ZERO would
#: mean this whole module had no population (Ruling 191), and that must fail.
CONTINUATION_FLOOR = 20


def continuation_lines(name: str) -> list[str]:
    """Every physical line in `docker/dev/<name>` that CONTINUES the line above it.

    ⛔ A COMMENT never continues anything, in any of these four files: Dockerfile's
    parser drops comment lines before it joins continuations, POSIX `sh` ends a
    comment at the newline regardless of a trailing backslash, and pip's
    requirements parser does the same. ⚠️ Getting that wrong would make
    `requirements.txt` look as though it had two continuation lines — its refresh
    recipe is a comment ending in `\\` — and the reading would be an artefact of
    this instrument rather than a fact about the file.
    """
    found = []
    continuing = False
    for line in read(name).splitlines():
        if continuing:
            found.append(line)
        comment = line.lstrip().startswith("#")
        continuing = not comment and line.rstrip("\n").endswith("\\")
    return found


def sites() -> dict[str, set[int]]:
    """Every decomposition site in `tests/docker/`, keyed `module::function`.

    ⭐ Derived from the AST rather than from a grep, so a site cannot hide behind a
    line break or a rename, and the enclosing function is the innermost one.

    ⛔ Every `*.py` in the directory and not just `test_*.py`: the readers they all
    share live in `devfiles.py`, and a glob that skipped it would exempt the one
    module whose whole job is reading these files.
    """
    found: dict[str, set[int]] = {}
    directory = repository_root() / "tests" / "docker"
    for path in sorted(directory.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        def visit(node: ast.AST, owner: str | None, module: Path = path) -> None:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                owner = node.name
            if isinstance(node, ast.Call):
                function = node.func
                decomposes = (
                    isinstance(function, ast.Attribute) and function.attr == "splitlines"
                ) or (isinstance(function, ast.Name) and function.id in COLLAPSING_READERS)
                if decomposes:
                    assert owner is not None, f"{module.name}:{node.lineno} is outside a function"
                    found.setdefault(f"{module.name}::{owner}", set()).add(node.lineno)
            for child in ast.iter_child_nodes(node):
                visit(child, owner)

        visit(tree, None)
    return found


def source_of(key: str) -> str:
    """The source text of the function a `module::function` key names."""
    module, _, name = key.partition("::")
    tree = ast.parse((repository_root() / "tests" / "docker" / module).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"{key} names no function")


# --- the population of readers, closed in both directions -------------------


def test_every_reader_of_the_dev_files_is_classified():
    # ⛔ The closed half of Ruling 258. A new `.splitlines()` over one of these
    # files is the defect `W131` swept, and the next person to write one is not
    # going to read this module first — so it fails their run instead.
    found = set(sites())
    declared = set(CLASSIFIED)
    assert found == declared, (
        f"the register of docker/dev/ readers is stale.\n"
        f"  classified but gone:  {sorted(declared - found)}\n"
        f"  present but unclassified: {sorted(found - declared)}\n"
        f"Add the site to CLASSIFIED with its verdict — `collapsed` if it reads "
        f"{COLLAPSING_READERS}, `line-anchored` only if its predicate matches at a "
        f"line START and its anchor is added to LINE_ANCHORS."
    )


def test_the_site_count_is_declared_so_a_second_one_cannot_hide():
    # ⚠️ `CLASSIFIED` is keyed by FUNCTION, so a second site added inside an
    # already-classified function would pass the check above. This is the other
    # dimension, and the unit is source lines.
    found = sites()
    total = sum(len(linenos) for linenos in found.values())
    assert total == DECOMPOSITION_SITES, (
        f"{total} decomposition site(s) in tests/docker/ and {DECOMPOSITION_SITES} "
        f"are declared: { ({key: sorted(value) for key, value in found.items()}) }"
    )


@pytest.mark.parametrize("key", sorted(k for k, v in CLASSIFIED.items() if v == "collapsed"))
def test_a_collapsed_site_really_collapses(key: str):
    # ⛔ The verdict is mechanical, not editorial: a site is `collapsed` only if its
    # own source reaches a collapsing reader or performs the collapse itself. A
    # comment claiming it does is worth nothing.
    source = source_of(key)
    reaches = [reader for reader in COLLAPSING_READERS if f"{reader}(" in source]
    assert reaches or COLLAPSE in source, (
        f"{key} is classified `collapsed` and neither calls {COLLAPSING_READERS} "
        f"nor performs the collapse itself"
    )


@pytest.mark.parametrize("key", sorted(k for k, v in CLASSIFIED.items() if v == "line-anchored"))
def test_a_line_anchored_site_really_anchors(key: str):
    # ⛔ The same rule the other way: `line-anchored` means the predicate is applied
    # to the start of a line, which in Python is `startswith`. A site that claims
    # the verdict with an `in` test is the exact defect this module swept.
    assert "startswith(" in source_of(key), (
        f"{key} is classified `line-anchored` but applies no start-of-line test"
    )


@pytest.mark.parametrize("key", sorted(k for k, v in CLASSIFIED.items() if v == "not-dev-text"))
def test_a_not_dev_text_site_reads_no_dev_file(key: str):
    # ⛔ The cheapest verdict to get wrong, because it exempts a site from every
    # assertion in this module. So it is checked: a site that reaches any reader of
    # `docker/dev/` is not exempt, whatever the comment beside it says.
    source = source_of(key)
    for reader in ("read(", "instructions(", "commands(", "joined("):
        assert reader not in source, (
            f"{key} is classified `not-dev-text` and calls {reader!r}, so it does read "
            f"{DEV}/ text and owes one of the other verdicts"
        )


@pytest.mark.parametrize("key", sorted(k for k, v in CLASSIFIED.items() if v == "no-continuations"))
def test_a_no_continuations_site_reads_only_a_file_that_has_none(key: str):
    # ⛔ The verdict rests on WHICH FILE is read, so that is what is checked. A site
    # that drifts onto `Dockerfile` or `check` — both of which do have continuations
    # — loses the ground it was exempted on, and loses it silently.
    source = source_of(key)
    assert any(name in source for name in CONTINUATION_FREE), (
        f"{key} is classified `no-continuations` and names none of {CONTINUATION_FREE}"
    )
    for name in ("Dockerfile", "check"):
        assert f'"{name}"' not in source, (
            f"{key} is classified `no-continuations` but reads {DEV}/{name}, which has "
            f"continuation lines. Collapse it with `commands()` or reclassify it."
        )


# --- and the verdict itself, asserted against the real files ----------------


def test_the_dev_files_actually_have_continuation_lines():
    # ⛔ Ruling 191: the two assertions below are vacuous on a file with no
    # continuations, and a vacuous check that reads green is worse than none. ⭐ The
    # browser's 22-package install is why the floor is comfortably met.
    found = continuation_lines("Dockerfile")
    assert len(found) >= CONTINUATION_FLOOR, (
        f"docker/dev/Dockerfile has {len(found)} continuation line(s), under the "
        f"floor of {CONTINUATION_FLOOR} — so every assertion in this module has "
        f"lost its population and `W131`'s sweep is no longer being checked"
    )


@pytest.mark.parametrize("name", sorted(LINE_ANCHORS))
def test_no_continuation_line_can_carry_a_line_anchored_predicate(name: str):
    # ⛔ **This is the whole of the `line-anchored` verdict, and it is a reading of
    # the file rather than an argument about grammar** (Ruling 220). The day somebody
    # writes a continuation line beginning `ARG ` or `- `, four checks above quietly
    # start reading a population that is missing a member — and this fails first,
    # naming the line.
    for line in continuation_lines(name):
        for anchor in LINE_ANCHORS[name]:
            assert not line.strip().startswith(anchor), (
                f"{DEV}/{name} has a CONTINUATION line beginning {anchor!r}: "
                f"{line.strip()!r}. Every site classified `line-anchored` against "
                f"that prefix is now reading physical lines for a construct that "
                f"no longer sits only at the start of one — collapse them with "
                f"`commands()` or move the line."
            )


@pytest.mark.parametrize("name", ("Dockerfile", "check"))
def test_no_comment_sits_inside_a_continued_instruction(name: str):
    # ⛔ **The `comment-filter` half.** `instructions()` drops comment lines one by
    # one, which is safe only while no comment sits BETWEEN a line ending in `\` and
    # the line it continues: dropping one there splices two unrelated fragments into
    # a single "instruction", and every check downstream then reads text that is in
    # no file.
    for line in continuation_lines(name):
        assert not line.lstrip().startswith("#"), (
            f"{DEV}/{name} has a comment inside a continued instruction: "
            f"{line.strip()!r}. instructions() would splice the fragments on either "
            f"side of it, and every check that reads this file would then assert "
            f"over text that appears nowhere in it."
        )


def test_commands_joins_text_that_raw_lines_keep_apart():
    # ⛔ The positive control for the remedy itself (Ruling 191). `commands()` is
    # only worth anything if it actually returns text spanning physical lines, and
    # the browser's install is the case the whole row turns on: `apt-get install` is
    # on one line and `libxrandr2` is six lines below it.
    installing = [command for command in commands("Dockerfile") if "apt-get install" in command]
    spanning = [
        command
        for command in installing
        if "ca-certificates" in command and "libxrandr2" in command
    ]
    assert spanning, (
        "no single element of commands('Dockerfile') carries both the first and the "
        "last package of the browser's install, so the continuation collapse is not "
        "happening and every check that depends on it is back to reading one "
        f"physical line. installing={installing}"
    )


def test_the_two_control_packages_are_still_on_different_lines():
    # ⛔ The NEGATIVE half of the control above, and without it that control proves
    # nothing: if `ca-certificates` and `libxrandr2` ever shared one physical line, a
    # raw-line reading would satisfy it too and the collapse could be removed
    # silently.
    raw = [
        line
        for line in read("Dockerfile").splitlines()
        if "ca-certificates" in line and "libxrandr2" in line
    ]
    assert not raw, (
        "the two packages the collapse control uses now share a PHYSICAL line, so "
        f"that control no longer distinguishes a collapsed reading from a raw one: "
        f"{raw}. Pick two packages that are still on different lines."
    )


def test_the_files_with_no_continuations_still_have_none():
    # ⛔ **The ground for four sites, stated rather than assumed.**
    # `requirement_names`, `test_every_tool_version_is_pinned_exactly` and
    # `test_the_visual_harness_variables_cross_into_the_container` read
    # `requirements.txt` and `compose.yaml` line by line, and the anchor check above
    # is VACUOUS for those two files because neither has a continuation at all. ⭐ So
    # that is the assertion: the day one appears, those sites need the collapse and
    # this says so rather than letting an empty population read as a pass.
    for name in CONTINUATION_FREE:
        assert continuation_lines(name) == [], (
            f"{DEV}/{name} now has continuation line(s) and the sites that read it "
            f"line by line were safe only because it had none. Collapse them with "
            f"`commands()`, or with `instructions(name).replace(chr(92) + chr(10), ' ')`."
        )
