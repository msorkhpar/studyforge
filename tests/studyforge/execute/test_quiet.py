"""Mirror of `src/studyforge/execute/quiet.py` (R12): `SF-29`'s acceptance, each clause both ways.

⭐ **The input is real output** (`transcripts.py` says where each line came
from). ⚠️ **Two inputs here are NOT captures, and each says so where it is
built:** a SPLICE, where a real program's lines are placed where surefire
prints a test's output, and the compiler plugin's SHAPE, which exists because
no real Maven compile error could be captured here (`SF-29/1`). The real
readings of both are `test_quiet_image.py`'s.

⭐ **Each test pulls one of two ways, because the filter can fail in either
direction:** it can show noise, which buries the answer, or it can hide the
signal, which is worse. So each drop rule is asserted by what survives it as
well as by what it removes.
"""

from __future__ import annotations

import dataclasses

import pytest

from studyforge.corpus.manifest.runtimes import RUNTIMES
from studyforge.execute import EXIT_STOPPED, EXIT_TIMEOUT, exit_line, quiet
from studyforge.execute.quiet import (
    EXIT_LINE,
    GRADLE,
    MAVEN,
    TOOLCHAINS,
    Quiet,
    Toolchain,
    filter_lines,
    select,
)
from tests.studyforge.execute.transcripts import (
    ALL,
    GRADLE_FAILURE,
    JAVAC_ERROR,
    JVM_TRACE,
    MAVEN_OFFLINE,
    MAVEN_OFFLINE_TRACE,
    MAVEN_PASS,
)

EVERY_FILTER = [pytest.param(MAVEN, id="maven"), pytest.param(GRADLE, id="gradle")]
EVERY_CHOICE = [*EVERY_FILTER, pytest.param(None, id="unfiltered")]


def run(transcript, code=0) -> list[str]:
    """A transcript as the runner streams it: every line, then its one exit line."""
    return [*transcript, exit_line(code)]


def shown(lines, toolchain=MAVEN) -> list[str]:
    return list(filter_lines(lines, toolchain))


def unedited_subsequence(kept: list[str], lines: list[str]) -> bool:
    """Is every kept line one of `lines`, byte for byte, in the order it came?"""
    remaining = iter(lines)
    return all(any(line == candidate for candidate in remaining) for line in kept)


def contiguous(block, lines: list[str]) -> bool:
    """Does `block` appear in `lines` whole, in order, and with nothing in between?"""
    block = list(block)
    return any(lines[i : i + len(block)] == block for i in range(len(lines) - len(block) + 1))


def maven_trace() -> list[str]:
    """Maven's own `-e` trace: from the exception line to its last frame, blank line included."""
    start = next(i for i, line in enumerate(MAVEN_OFFLINE_TRACE) if "Exception: " in line)
    end = max(i for i, line in enumerate(MAVEN_OFFLINE_TRACE) if line.startswith("    at "))
    return list(MAVEN_OFFLINE_TRACE[start : end + 1])


def spliced() -> list[str]:
    """⚠️ A SPLICE, not a capture: `JVM_TRACE`'s real lines placed where surefire prints a
    test's output, between `Running <class>` and that class's tally, unprefixed."""
    at = MAVEN_PASS.index("[INFO] Running smoke.AdderTest") + 1
    return [*MAVEN_PASS[:at], *JVM_TRACE, *MAVEN_PASS[at:]]


#: ⚠️ The compiler plugin's SHAPE, NOT a capture (`SF-29/1`): its `[ERROR]` line
#: and the unprefixed continuation lines it prints beneath it. The rules keep it
#: whatever the exact wording is. `test_quiet_image.py` reads the real one.
COMPILER_PLUGIN_SHAPE = (
    "[ERROR] COMPILATION ERROR : ",
    "[ERROR] src/main/java/smoke/Adder.java:[5,20] cannot find symbol",
    "  symbol:   variable c",
    "  location: class smoke.Adder",
    "[INFO] 1 error",
)


# --- a Maven test run is reduced to program output plus verdict ---------------------------


def test_a_maven_test_run_is_reduced_to_its_verdict():
    assert shown(run(MAVEN_PASS)) == [
        "[INFO] Running smoke.AdderTest",
        "[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.020 s "
        "-- in smoke.AdderTest",
        "[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0",
        exit_line(0),
    ]


def test_without_a_filter_the_same_run_keeps_every_banner():
    """The other way: the build tool's own lines ARE there to drop."""
    assert shown(run(MAVEN_PASS), None) == run(MAVEN_PASS)
    assert "[INFO] BUILD SUCCESS" in MAVEN_PASS
    assert "[INFO] BUILD SUCCESS" not in shown(run(MAVEN_PASS))


def test_a_programs_own_output_survives_a_maven_run_whole():
    lines = shown(run(spliced()))
    assert contiguous(JVM_TRACE, lines)
    assert lines == [
        "[INFO] Running smoke.AdderTest",
        *JVM_TRACE,
        *[line for line in MAVEN_PASS if "Tests run:" in line],
        exit_line(0),
    ]


def test_a_maven_failure_keeps_why_it_failed_and_drops_how_to_rerun_maven():
    assert shown(run(MAVEN_OFFLINE, 1)) == [
        "[WARNING] The POM for org.apache.maven.plugins:maven-resources-plugin:jar:3.4.0 "
        "is missing, no dependency information available",
        *[line for line in MAVEN_OFFLINE if "could not be resolved" in line],
        *[line for line in MAVEN_OFFLINE if line.startswith("[ERROR] \tCannot access")],
        exit_line(1),
    ]


def test_the_help_footer_is_in_the_transcript_to_drop():
    """The other way: the dropped `[ERROR]` lines exist, and `signal` alone would keep them."""
    footer = [line for line in MAVEN_OFFLINE if "[Help 1]" in line or "-X switch" in line]
    assert len(footer) >= 3
    no_footer_rule = dataclasses.replace(MAVEN, always_noise=())
    assert all(Quiet(no_footer_rule).keeps(line) for line in footer)
    assert not any(Quiet(MAVEN).keeps(line) for line in footer)


# --- a compile error survives filtering intact --------------------------------------------


@pytest.mark.parametrize("toolchain", EVERY_CHOICE)
def test_a_compile_error_survives_intact(toolchain):
    lines = shown(run(JAVAC_ERROR, 1), toolchain)
    assert contiguous(JAVAC_ERROR, lines)


def test_the_compiler_plugins_error_form_survives_intact_in_a_maven_run():
    at = (
        MAVEN_PASS.index(
            "[INFO] Compiling 1 source file with javac [debug release 21] to target/classes"
        )
        + 1
    )
    lines = shown(run([*MAVEN_PASS[:at], *COMPILER_PLUGIN_SHAPE], 1))
    assert contiguous(COMPILER_PLUGIN_SHAPE, lines)


def test_what_keeps_a_compile_error_is_a_rule_and_its_removal_would_show():
    """The other way: a noise rule that named these lines WOULD drop them — so the
    `[ERROR]` signal, and naming no unprefixed line, are what keep them."""
    greedy = dataclasses.replace(MAVEN, signal=(), noise=(*MAVEN.noise, r"^\[ERROR\]", "error"))
    assert not contiguous(COMPILER_PLUGIN_SHAPE, shown(COMPILER_PLUGIN_SHAPE, greedy))
    assert not contiguous(JAVAC_ERROR, shown(JAVAC_ERROR, greedy))


def test_gradle_keeps_a_compile_error_and_drops_a_warning():
    lines = shown(
        [
            "e: src/A.kt:5:9 Unresolved reference 'fruitCont'",
            "w: src/A.kt:2:5 Variable is never used",
            exit_line(1),
        ],
        GRADLE,
    )
    assert lines == ["e: src/A.kt:5:9 Unresolved reference 'fruitCont'", exit_line(1)]


# --- a stack trace survives intact --------------------------------------------------------


@pytest.mark.parametrize("toolchain", EVERY_CHOICE)
def test_a_programs_stack_trace_survives_intact(toolchain):
    assert contiguous(JVM_TRACE, shown(run(JVM_TRACE, 1), toolchain))


def test_mavens_own_stack_trace_survives_intact_blank_line_and_all():
    trace = maven_trace()
    assert "" in trace and any(line.startswith("\t") for line in trace)
    assert contiguous(trace, shown(run(MAVEN_OFFLINE_TRACE, 1)))


def test_every_frame_of_a_gradle_trace_survives_not_only_the_readers():
    """⚠️ The extraction source kept one frame of these six. The epic says intact."""
    frames = [line for line in GRADLE_FAILURE if line.lstrip().startswith("at ")]
    assert len(frames) == 6
    assert [line for line in shown(GRADLE_FAILURE, GRADLE) if line in frames] == frames


def test_no_toolchain_rule_can_reach_a_stack_frame():
    """The noise planted here names every frame, and the frames survive it."""
    hostile = dataclasses.replace(MAVEN, always_noise=(r"^\s+at ", r"^Caused by", r"more$"))
    assert contiguous(JVM_TRACE, shown(JVM_TRACE, hostile))


def test_without_the_stack_trace_rule_the_same_plant_would_drop_the_frames(monkeypatch):
    """The other way: the frames survive because `STACK_TRACE` is checked first."""
    monkeypatch.setattr(quiet, "STACK_TRACE", ())
    hostile = dataclasses.replace(MAVEN, always_noise=(r"^\s+at ", r"^Caused by", r"more$"))
    assert not contiguous(JVM_TRACE, shown(JVM_TRACE, hostile))


def test_the_intactness_check_is_not_blind():
    """The other way, for the instrument itself: a lost frame or a gap is caught."""
    lines = list(JVM_TRACE)
    assert contiguous(JVM_TRACE, lines)
    assert not contiguous(JVM_TRACE, lines[:2] + lines[3:])
    assert not contiguous(JVM_TRACE, [*lines[:2], "noise", *lines[2:]])


# --- selectable per toolchain; unknown passes through -------------------------------------


@pytest.mark.parametrize(
    ("declared", "expected"),
    [
        (("java", "maven"), MAVEN),
        (("maven", "java"), MAVEN),
        (("gradle", "java", "kotlin"), GRADLE),
    ],
)
def test_the_declared_build_tool_selects_its_filter(declared, expected):
    assert select(declared) is expected


@pytest.mark.parametrize(
    "declared",
    [
        (),
        ("python",),
        ("java",),
        ("node", "shell", "sqlite"),
        ("ant",),
        ("gradle", "java", "maven"),
    ],
    ids=["undeclared", "python", "java-only", "no-build-tool", "unknown", "two-build-tools"],
)
def test_an_unknown_undeclared_or_ambiguous_toolchain_selects_nothing(declared):
    assert select(declared) is None


@pytest.mark.parametrize("name", list(ALL))
def test_no_filter_passes_every_line_through_untouched(name):
    assert shown(run(ALL[name], 1), select(())) == run(ALL[name], 1)


@pytest.mark.parametrize(
    ("toolchain", "transcript"), [(MAVEN, MAVEN_PASS), (GRADLE, GRADLE_FAILURE)], ids=["mvn", "gr"]
)
def test_a_selected_filter_does_drop_lines(toolchain, transcript):
    """The other way: the pass-through above is a property of `None`, not of the input."""
    assert len(shown(run(transcript), toolchain)) < len(run(transcript))


def test_each_build_tool_gets_its_own_rules_and_not_the_others():
    assert "> Task :jvm:kotlin:compileKotlin UP-TO-DATE" in shown(GRADLE_FAILURE, MAVEN)
    assert "> Task :jvm:kotlin:compileKotlin UP-TO-DATE" not in shown(GRADLE_FAILURE, GRADLE)
    assert "[INFO] BUILD SUCCESS" in shown(MAVEN_PASS, GRADLE)
    assert "[INFO] BUILD SUCCESS" not in shown(MAVEN_PASS, MAVEN)


def test_every_filter_is_named_for_a_runtime_a_corpus_can_declare():
    assert all(name in RUNTIMES and TOOLCHAINS[name].name == name for name in TOOLCHAINS)
    assert "ant" not in RUNTIMES


def test_a_new_toolchain_is_one_entry_of_data(monkeypatch):
    """Declared, not hardcoded: a rule set added to the table is selected and applied."""
    assert select(("node",)) is None
    node = Toolchain(name="node", always_noise=(), signal=(), noise=(r"^npm notice ",))
    monkeypatch.setitem(TOOLCHAINS, "node", node)
    assert select(("node",)) is node
    assert shown(["npm notice New version", "3 passing", exit_line(0)], node) == [
        "3 passing",
        exit_line(0),
    ]


# --- what holds of every filter -----------------------------------------------------------


@pytest.mark.parametrize("toolchain", EVERY_CHOICE)
@pytest.mark.parametrize("name", list(ALL))
def test_a_kept_line_is_never_edited_or_reordered(toolchain, name):
    lines = run(ALL[name], 1)
    assert unedited_subsequence(shown(lines, toolchain), lines)


def test_the_subsequence_check_is_not_blind():
    lines = ["a", "b", "c"]
    assert unedited_subsequence(["a", "c"], lines)
    assert not unedited_subsequence(["a", "B"], lines)
    assert not unedited_subsequence(["c", "a"], lines)


@pytest.mark.parametrize("toolchain", EVERY_FILTER)
@pytest.mark.parametrize("code", [0, 1, 127, EXIT_TIMEOUT, EXIT_STOPPED])
def test_the_exit_line_always_survives(toolchain, code):
    assert shown([exit_line(code)], toolchain) == [exit_line(code)]


def test_the_exit_line_rule_matches_the_runners_spelling_and_nothing_looser():
    import re

    assert re.fullmatch(EXIT_LINE, exit_line(0))
    assert not re.search(EXIT_LINE, "--- exit ---")
    assert not re.search(EXIT_LINE, "[INFO] --- surefire:3.5.4:test (default-test) @ smoke ---")


def test_lines_are_filtered_as_they_arrive_not_after_the_run():
    """A page shows a line when it is written, so the filter must not wait for the end."""
    consumed = []

    def stream():
        for line in run(spliced()):
            consumed.append(line)
            yield line

    first = next(filter_lines(stream(), MAVEN))
    assert first == "[INFO] Running smoke.AdderTest"
    assert consumed[-1] == first and len(consumed) < len(run(spliced()))


# --- the Gradle rules, ported: what the reader called valueless goes ----------------------


@pytest.mark.parametrize(
    "noise",
    [
        "> Task :jvm:kotlin:compileKotlin UP-TO-DATE",
        "> Task :jvm:kotlin:test FAILED",
        "BUILD FAILED in 2s",
        "4 actionable tasks: 2 executed, 2 up-to-date",
        "FAILURE: Build failed with an exception.",
        "* What went wrong:",
        "Execution failed for task ':jvm:kotlin:test'.",
        "* Try:",
        "> Run with --scan to get full insights from a Build Scan (powered by Develocity).",
        "Consider enabling configuration cache to speed up this build: "
        "https://docs.gradle.org/9.7.1/userguide/configuration_cache_enabling.html",
    ],
)
def test_gradles_own_lines_go(noise):
    assert shown([noise, exit_line(1)], GRADLE) == [exit_line(1)]


def test_gradle_keeps_the_verdict_the_assertion_and_the_tests_own_output():
    lines = shown(GRADLE_FAILURE, GRADLE)
    assert "9 tests completed, 3 failed" in lines
    assert any(line.endswith("prints() FAILED") for line in lines)
    assert any(
        "AssertionFailedError: KitchenInventoryManagement printed nothing." in line
        for line in lines
    )
    assert any(line.endswith("STANDARD_OUT") for line in lines)


# --- Maven's rerun advice: every footer rule, named by its line ---------------------------

#: The offline capture carries the first four. ⚠️ The rest are Maven's and surefire's
#: wording, as the rules name them, and not a capture: a reactor build's resume hint
#: and surefire's report and dump notices.
FOOTER = (
    "[ERROR] ",
    "[ERROR] -> [Help 1]",
    "[ERROR] Re-run Maven using the -X switch to enable full debug logging.",
    "[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/PluginResolutionException",
    "[ERROR] After correcting the problems, you can resume the build with the command",
    "[ERROR]   mvn <args> -rf :smoke",
    "[ERROR] Please refer to target/surefire-reports for the individual test results.",
    "[ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump",
)


@pytest.mark.parametrize("line", FOOTER)
def test_every_footer_rule_drops_its_line_and_only_that(line):
    assert not Quiet(MAVEN).keeps(line)
    assert Quiet(dataclasses.replace(MAVEN, always_noise=())).keeps(line)


# --- signal beats noise: a line that matches BOTH is kept ---------------------------------

#: ⚠️ CONSTRUCTED lines, not captures: none of the real transcripts carries a line that
#: matches both lists, which is why this clause needs its own input. Each line is checked
#: below to match at least one `signal` AND one `noise` pattern of its toolchain.
BOTH = [
    pytest.param(
        MAVEN, "[INFO] --- Tests run: 3, Failures: 1, Errors: 0, Skipped: 0 ---", id="mvn"
    ),
    pytest.param(
        GRADLE, "warning: java.lang.IllegalStateException: config was not read", id="gr-warn"
    ),
    pytest.param(
        GRADLE, "e: src/A.kt:5:9 see https://docs.gradle.org/current/userguide/x.html", id="gr-e"
    ),
    pytest.param(
        GRADLE, "Consider enabling AssertionFailedError: expected 3 but was 2", id="gr-assert"
    ),
]


def matches(patterns, line) -> bool:
    import re

    return any(re.search(pattern, line) for pattern in patterns)


@pytest.mark.parametrize(("toolchain", "line"), BOTH)
def test_a_line_matching_both_signal_and_noise_is_kept(toolchain, line):
    assert matches(toolchain.signal, line) and matches(toolchain.noise, line)
    assert not matches(toolchain.always_noise, line)
    assert shown([line, exit_line(1)], toolchain) == [line, exit_line(1)]


@pytest.mark.parametrize(("toolchain", "line"), BOTH)
def test_without_the_signal_rule_the_same_line_would_be_dropped(toolchain, line):
    """The other way: it is `signal`, checked before `noise`, that keeps it."""
    assert shown([line, exit_line(1)], dataclasses.replace(toolchain, signal=())) == [exit_line(1)]
