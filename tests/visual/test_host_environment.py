"""No VERDICT in this package is reached from the HOST's environment silently.

⛔ **No verdict may depend on the host silently (R15).** ⭐ A git call that takes
its population from the host is one way a verdict can; ⚠️ **this module guards a
different mechanism: an environment variable crossing the host boundary into
`tests/visual/`, which a guard that reads git calls cannot see.**

## ⛔ THE UNIT, NAMED, AND NEVER A BARE COUNT

⛔ **The subject is *the distinct `STUDYFORGE_*` names that `tests/visual/`
reads*.** ⚠️ **A bare `3` or `4` cannot identify which population is meant**: a
count can be right in MAGNITUDE and wrong in MEMBERSHIP. ⭐ **So `POPULATION`
below names every one, with the FUNCTION that reads it, and the partition is
asserted over the code rather than over this prose.**

## ⛔ WHAT THIS IS NOT: a removal of `STUDYFORGE_VISUAL=required`

⭐ **That variable is the whole of how the harness refuses to be a check that
cannot fail.** ⛔ **What is forbidden is a verdict depending on it silently**, so
there are exactly two arms and every verdict-reaching name takes one of them:

| arm | what it means | where |
|---|---|---|
| ⭐ **FIXTURE** | the TEST decides the environment | `pinned_environment` |
| ⭐ **LICENCE** | it may read the host and SAYS SO | `conftest.py` |

⚠️ **A NAMED module with a STATED licence, never a pattern** — a list of named
readers, each with its licence, is the shape.

## ⛔ The shape of the defect this sweep refuses

⭐ A test that fakes the browser's ABSENCE and then lets the HOST decide whether
absence skips or fails passes with `STUDYFORGE_VISUAL` unset and fails with
`STUDYFORGE_VISUAL=required`, on the same tree. ⚠️ It is a class rather than one
bug, which is why the guard below is a sweep and not a fix to one test.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.visual import conftest, discovery

HERE = Path(__file__).parent

#: ⛔ **The whole population, MEASURED and then DECLARED**: every `STUDYFORGE_*`
#: name this package reads from `os.environ`, mapped to the single function that
#: reads it. ⭐ **One reader each, deliberately** — a second reader of the same
#: variable is a second spelling of the same decision, which is how a run comes
#: to PRINT one verdict and ACT on another.
POPULATION = {
    "STUDYFORGE_VISUAL": "discovery.demand_is_in_force",
    "STUDYFORGE_VISUAL_BROWSER": "discovery.state",
    "STUDYFORGE_DEV_CONTAINER": "discovery.evidence_state",
    "STUDYFORGE_VISUAL_CAPTURES": "conftest.capture_dir",
}

#: ⛔ **The three that reach a VERDICT**.
#: ⚠️ `STUDYFORGE_DEV_CONTAINER` is the STRONGEST member rather
#: than an afterthought: it decides `evidence_state()`, which is the
#: ADMISSIBILITY of every reading this harness takes.
VERDICT_REACHING = (
    "STUDYFORGE_VISUAL",
    "STUDYFORGE_VISUAL_BROWSER",
    "STUDYFORGE_DEV_CONTAINER",
)

#: ⭐ **The one that reaches an ARTIFACT and no verdict**: its only effect is
#: where the PNGs land. ⛔ A declared set that included it would be wrong
#: in the other direction.
ARTIFACT_ONLY = ("STUDYFORGE_VISUAL_CAPTURES",)

#: ⛔ **The module that DEFINES the readings, excluded from the ambient sweep
#: below because it is where the environment is read ON PURPOSE.** ⭐ Its verdicts
#: are asserted over a fixture here; the sweep's subject is who CALLS them.
DEFINES_THE_READINGS = ("discovery.py",)

#: ⛔ **The ONE module licensed to hand the AMBIENT environment to a verdict
#: function, and the licence is stated rather than assumed.** ⭐ `conftest.py`'s
#: `browser` fixture and `pytest_terminal_summary` ARE the harness: the verdict
#: they can reach is a SKIP or a FAILURE that names itself and its remedy,
#: the count of what did not run is printed, and the environment in
#: force is printed beside it. ⚠️ **Nothing there can turn a silent non-run into
#: a green reading** — which is the property `LIVE_ROOT_READERS` states for the
#: git half, in the same form.
AMBIENT_ENVIRONMENT_READERS = ("conftest.py",)

#: ⛔ The readings whose answer an environment variable changes. ⚠️ **Matched on
#: the LAST SEGMENT**, so `discovery.state(...)` and a bare `state(...)` are both
#: reached — a superset matcher, and its reach is declared here.
VERDICT_FUNCTIONS = (
    "require_browser",
    "state",
    "evidence_state",
    "report_line",
    "environment_declaration",
    "demand_is_in_force",
)

#: The fixture that pins the environment, so a test decides it rather than the host.
PINNING_FIXTURE = "pinned_environment"


# --- the instrument -----------------------------------------------------------


def _dotted(node: ast.expr) -> str:
    """`os.environ.get` for an attribute chain, `state` for a bare name, `""` otherwise."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def _string_constants(tree: ast.Module) -> dict[str, str]:
    """Module-level `NAME = "literal"` bindings, so a read through a constant resolves."""
    return {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    }


def _environment_key(node: ast.AST, bindings: dict[str, str]) -> str | None:
    """The `STUDYFORGE_*` name this node reads from the environment, if it reads one."""
    key: ast.expr | None = None
    if isinstance(node, ast.Call) and _dotted(node.func).endswith("environ.get") and node.args:
        key = node.args[0]
    elif isinstance(node, ast.Subscript) and _dotted(node.value).endswith("environ"):
        key = node.slice
    if key is None:
        return None
    if isinstance(key, ast.Constant) and isinstance(key.value, str):
        name = key.value
    elif isinstance(key, ast.Name):
        name = bindings.get(key.id, "")
    else:
        return None
    return name if name.startswith("STUDYFORGE_") else None


def _environment_reads(node: ast.AST, bindings: dict[str, str], where: str) -> dict[str, str]:
    """Every `STUDYFORGE_*` environment read under `node`, mapped to its enclosing function.

    ⚠️ **What it does NOT cover, DECLARED rather than implied**, as a closed
    list: a name rebound through a second constant, a key built at run
    time, a read through `os.getenv`, and a read in a module this package
    imports rather than contains. ⛔ **Nothing in this package does any of the
    four, and that is a measurement rather than a hope** — a guard claiming a
    reach it has not got is the defect it guards against.
    """
    found: dict[str, str] = {}
    for child in ast.iter_child_nodes(node):
        name = _environment_key(child, bindings)
        if name:
            found[name] = where
        inner = child.name if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef) else where
        found.update(_environment_reads(child, bindings, inner))
    return found


def _reads_the_environment(source: str, stem: str) -> dict[str, str]:
    """`STUDYFORGE_*` name -> `<module stem>.<function>`, for one module's source."""
    tree = ast.parse(source)
    reads = _environment_reads(tree, _string_constants(tree), "<module>")
    return {name: f"{stem}.{where}" for name, where in reads.items()}


def _calls(node: ast.AST) -> set[str]:
    """The last segment of every call spelled anywhere under `node`."""
    return {
        _dotted(child.func).split(".")[-1]
        for child in ast.walk(node)
        if isinstance(child, ast.Call) and _dotted(child.func)
    }


def _pytest_runs_it(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether pytest itself calls this function: a test, a fixture, or a hook.

    ⛔ **The distinction is load-bearing.** ⚠️ A plain module-level helper cannot
    request a fixture — it is called with arguments by its neighbours — so
    demanding one of `test_init.py`'s `_line_for(state)` would be a check
    that fires on correct work.
    ⭐ **A helper CONTRIBUTES REACH and is never itself the offender; the function
    pytest runs is the one that owes the fixture.**

    ⛔ **BOTH decorator spellings.** ⚠️ `@pytest.fixture` is an
    `ast.Name`/`ast.Attribute` and `@pytest.fixture(scope="session")` is an
    `ast.Call`, so a predicate that took the dotted spelling of the node itself
    would score `conftest.browser` — the LICENSED positive row, and the most
    important fixture in the package — as something pytest does not run. ⭐ **The
    plant below holds both spellings.**
    """
    if node.name.startswith(("test_", "pytest_")):
        return True
    for decorator in node.decorator_list:
        spelled = decorator.func if isinstance(decorator, ast.Call) else decorator
        if _dotted(spelled).split(".")[-1] == "fixture":
            return True
    return False


def _uncontrolled_verdict_callers(source: str) -> list[str]:
    """What pytest runs here that reaches a verdict without pinning the environment.

    ⭐ **It follows ONE level of module-local helper**, because the shape people
    actually write is a `_line_for(state)` beside the test — and a predicate that
    only saw the direct call would have scored `test_init.py` clean while its
    helper called `report_line()` on the host's environment.

    ⚠️ **Declared gaps**, a closed list: a helper two levels down, a
    helper imported from another module, a verdict reached through a fixture
    this sweep does not resolve, a callable spelled outside `VERDICT_FUNCTIONS`,
    and a test that pins the environment some other way than by requesting
    `pinned_environment`. ⛔ **Nothing in this package does any of the five, and
    that is a measurement rather than a hope.**
    """
    tree = ast.parse(source)
    functions = [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    ]
    direct = {node.name for node in functions if _calls(node) & set(VERDICT_FUNCTIONS)}
    reaching = set(VERDICT_FUNCTIONS) | direct
    offenders = []
    for node in functions:
        if not _pytest_runs_it(node) or not _calls(node) & reaching:
            continue
        arguments = {argument.arg for argument in node.args.args}
        if PINNING_FIXTURE not in arguments:
            offenders.append(node.name)
    return sorted(offenders)


def _sources(only: str = "*.py") -> dict[str, str]:
    """Every module in this package matching `only`, by file name."""
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(HERE.glob(only))}


# --- the population, and its partition ----------------------------------------


def test_every_environment_variable_this_package_reads_is_DECLARED_and_PARTITIONED() -> None:
    """⛔ The population is measured from the code, never inherited from prose.

    ⭐ **Red four ways**: a new `STUDYFORGE_*` name, a name that stops being
    read, a read that MOVES into another function, and a second reader of a name
    that had one.
    """
    sources = _sources()
    assert len(sources) >= 10, f"born vacuous: the package has {len(sources)} modules"
    measured: dict[str, str] = {}
    for name, text in sources.items():
        for variable, where in _reads_the_environment(text, Path(name).stem).items():
            assert variable not in measured, (
                f"⛔ {variable} is read by BOTH {measured.get(variable)} and {where}. "
                f"One reader per variable: a second spelling of the same decision is how "
                f"a run PRINTS one verdict and ACTS on another."
            )
            measured[variable] = where
    assert measured == POPULATION, (
        f"⛔ this package reads {sorted(measured)} and declares {sorted(POPULATION)}. "
        f"A committed verdict may not depend on the host's environment SILENTLY "
        f"(R15): declare the name here, put it in VERDICT_REACHING "
        f"or ARTIFACT_ONLY, and — if it reaches a verdict — name it in "
        f"discovery.environment_declaration() so every run prints the value in force."
    )


def test_the_partition_is_TOTAL_and_DISJOINT_over_the_declared_population() -> None:
    """⛔ A declared list is a CLOSED claim, so a partial one is worse than none."""
    assert set(VERDICT_REACHING) | set(ARTIFACT_ONLY) == set(POPULATION)
    assert not set(VERDICT_REACHING) & set(ARTIFACT_ONLY)
    assert ARTIFACT_ONLY, "⛔ a partition with an empty half is a list, not a partition"
    assert set(VERDICT_REACHING) == {
        "STUDYFORGE_VISUAL",
        "STUDYFORGE_VISUAL_BROWSER",
        "STUDYFORGE_DEV_CONTAINER",
    }, (
        "⭐ the verdict-reaching subset of the distinct STUDYFORGE_* names "
        "tests/visual/ reads — named by its MEMBERS and never by a count: it "
        "includes the container marker and excludes the capture directory"
    )


# --- each verdict-reaching member, asserted over a FIXTURE ---------------------


def test_STUDYFORGE_VISUAL_reaches_its_verdict_in_BOTH_directions(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ Absence is a SKIP or a FAILURE, and the TEST decides which — not the host."""
    absent = discovery.State(binary=None, version=None, searched=discovery.CANDIDATES)
    monkeypatch.setattr(discovery, "state", lambda: absent)
    assert discovery.demand_is_in_force() is False
    with pytest.raises(pytest.skip.Exception):
        discovery.require_browser()
    monkeypatch.setenv(discovery.DEMAND_VARIABLE, discovery.DEMAND_VALUE)
    assert discovery.demand_is_in_force() is True
    with pytest.raises(pytest.fail.Exception):
        discovery.require_browser()


def test_STUDYFORGE_VISUAL_BROWSER_reaches_its_verdict_in_BOTH_directions(
    pinned_environment, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """⛔ WHICH ENGINE produced every reading, and it is asserted off this machine's PATH.

    ⭐ `shutil.which` is faked, so the reading is the same on a host with Chrome,
    a host without one, and inside the pinned image.
    """
    on_path = tmp_path / "chromium"
    named = tmp_path / "named-engine"
    for binary in (on_path, named):
        binary.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(discovery, "_version_of", lambda binary: "Faked Engine 9.9")
    monkeypatch.setattr(
        discovery.shutil, "which", lambda candidate: str(on_path) if candidate else None
    )
    discovery.state.cache_clear()
    from_path = discovery.state()
    assert from_path.binary == str(on_path)
    assert from_path.named is False
    monkeypatch.setenv(discovery.BINARY_VARIABLE, str(named))
    discovery.state.cache_clear()
    from_variable = discovery.state()
    assert from_variable.binary == str(named)
    assert from_variable.named is True
    assert from_path.binary != from_variable.binary, "⛔ the two readings must DIFFER"


def test_STUDYFORGE_DEV_CONTAINER_reaches_the_ADMISSIBILITY_verdict_in_BOTH_directions(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ The STRONGEST member: it decides what evidence state a reading may CLAIM."""
    assert discovery.evidence_state().startswith("unpinned")
    monkeypatch.setenv(discovery.CONTAINER_VARIABLE, "1")
    assert discovery.evidence_state().startswith("pinned")
    for not_the_marker in ("", "0", "yes", "true", "TRUE"):
        monkeypatch.setenv(discovery.CONTAINER_VARIABLE, not_the_marker)
        assert discovery.evidence_state().startswith("unpinned"), not_the_marker


def test_the_ARTIFACT_ONLY_variable_reaches_NO_verdict_and_that_is_the_CONTROL(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ The partition is a claim until its other half is exercised.

    ⛔ Flipping `STUDYFORGE_VISUAL_CAPTURES` must change NONE of the three
    verdicts and must not appear in the declaration — otherwise `ARTIFACT_ONLY`
    is a label rather than a measurement.
    """
    before = (
        discovery.demand_is_in_force(),
        discovery.evidence_state(),
        discovery.environment_declaration(),
    )
    for value in ("/tmp/captures", "", "1"):
        monkeypatch.setenv(ARTIFACT_ONLY[0], value)
        assert (
            discovery.demand_is_in_force(),
            discovery.evidence_state(),
            discovery.environment_declaration(),
        ) == before
    assert ARTIFACT_ONLY[0] not in discovery.environment_declaration()


# --- the declaration: every verdict-reaching member is PRINTED -----------------


def test_every_VERDICT_REACHING_name_is_PRINTED_by_the_line_every_run_writes(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ The LICENCE arm: the dependence is admissible because the run SAYS it.

    ⭐ Asserted over the whole cross-product, so the declaration cannot be right
    on this machine's combination and wrong on the other seven.
    """
    present = discovery.State(
        binary="/some/browser", version="Some Browser 1.2", searched=(), named=True
    )
    monkeypatch.setattr(discovery, "state", lambda: present)
    for demand in (None, discovery.DEMAND_VALUE):
        for container in (None, "1"):
            for captures in (None, "/tmp/captures"):
                for variable, value in (
                    (discovery.DEMAND_VARIABLE, demand),
                    (discovery.CONTAINER_VARIABLE, container),
                    (ARTIFACT_ONLY[0], captures),
                ):
                    if value is None:
                        monkeypatch.delenv(variable, raising=False)
                    else:
                        monkeypatch.setenv(variable, value)
                declaration = discovery.environment_declaration()
                for name in VERDICT_REACHING:
                    assert f"${name}" in declaration, (name, declaration)
                assert ARTIFACT_ONLY[0] not in declaration
                assert declaration in discovery.report_line(0), "⛔ the RAN branch"
                demanded = f"${discovery.DEMAND_VARIABLE}={discovery.DEMAND_VALUE}"
                assert (demanded in declaration) == (demand is not None)
                assert (f"${discovery.CONTAINER_VARIABLE}=1" in declaration) == (container == "1")


def test_the_NO_BROWSER_branch_carries_the_declaration_too(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ The branch that matters most: a run that did nothing says what it did nothing UNDER."""
    absent = discovery.State(binary=None, version=None, searched=discovery.CANDIDATES)
    monkeypatch.setattr(discovery, "state", lambda: absent)
    line = discovery.report_line(123)
    assert "NO BROWSER" in line
    assert "123 visual check(s) DID NOT RUN" in line
    assert discovery.environment_declaration() in line


def test_the_declaration_prints_a_STATE_and_never_a_PATH(
    pinned_environment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ R7: `$STUDYFORGE_VISUAL_BROWSER` holds a path, and a path is somebody's home.

    ⚠️ The value is built at run time from an obvious placeholder account, because
    spelling a home-shaped path as one literal would be a finding against this
    very file.
    """
    home_shaped = "/" + "home" + "/" + "jane-doe" + "/engines/chromium"
    monkeypatch.setenv(discovery.BINARY_VARIABLE, home_shaped)
    monkeypatch.setenv(ARTIFACT_ONLY[0], home_shaped + "/captures")
    discovery.state.cache_clear()
    for line in (discovery.environment_declaration(), discovery.report_line(1)):
        assert home_shaped not in line, "⛔ a VALUE reached the line a run prints"
        assert "jane-doe" not in line


# --- the sweep: no test here lets the AMBIENT environment reach a verdict ------


def test_no_TEST_in_this_package_lets_the_AMBIENT_environment_reach_a_VERDICT() -> None:
    """⛔ The enforcement arm: no test lets the ambient environment reach a verdict.

    ⭐ **The population is every module in this package EXCEPT the one that
    DEFINES the readings**, which is named in `DEFINES_THE_READINGS` and reads
    the environment on purpose. ⛔ **The one licensed caller is
    `AMBIENT_ENVIRONMENT_READERS`, and it doubles as this guard's POSITIVE ROW:
    the reading is `1` against a declared `1`, never `0` against `0`.**
    """
    sources = _sources()
    for declared in (*DEFINES_THE_READINGS, *AMBIENT_ENVIRONMENT_READERS):
        assert declared in sources, f"⛔ {declared} is declared here and does not exist"
    for definer in DEFINES_THE_READINGS:
        sources.pop(definer)
    assert len(sources) >= 10, f"born vacuous: {len(sources)} modules after the exclusion"
    reading = {
        name: found
        for name, text in sources.items()
        if (found := _uncontrolled_verdict_callers(text))
    }
    assert sorted(reading) == sorted(AMBIENT_ENVIRONMENT_READERS), (
        f"⛔ {reading} reach a verdict from the AMBIENT environment. A committed "
        f"verdict may not depend on the host's environment (R15): such a test reads "
        f"a SKIP with $STUDYFORGE_VISUAL unset and a FAILURE with it set, on the same "
        f"tree. "
        f"⭐ Request the `{PINNING_FIXTURE}` fixture and decide the environment, or "
        f"state a licence here the way {AMBIENT_ENVIRONMENT_READERS[0]} does."
    )


def test_the_AMBIENT_guard_is_PLANTED_in_both_directions_and_the_two_readings_DIFFER() -> None:
    """⛔ The guard above is validated by PLANTING, not only by running.

    ⭐ **Nine readings.** The PLANTS are the retired shape in every spelling
    pytest runs — a test, a fixture, a hook, and a test reached through a
    one-level helper — and the IMPOSSIBLE readings are the four that must stay
    silent: a controlled test, the HELPER ITSELF (which cannot request a
    fixture), a function that calls nothing verdict-shaped, and this module's own
    prose mention.
    """
    direct = "def test_x():\n    discovery.require_browser()\n"
    fixture = "@pytest.fixture\ndef browser():\n    discovery.require_browser()\n"
    called = '@pytest.fixture(scope="session")\ndef browser():\n    discovery.require_browser()\n'
    hook = "def pytest_terminal_summary(r):\n    r.write_line(discovery.report_line(1))\n"
    helper = "def _line():\n    return discovery.report_line(1)\n\ndef test_x():\n    _line()\n"
    controlled = f"def test_x({PINNING_FIXTURE}):\n    discovery.require_browser()\n"
    helper_only = "def _line():\n    return discovery.report_line(1)\n"
    innocent = "def test_x():\n    assert 1 == 1\n"
    assert _uncontrolled_verdict_callers(direct) == ["test_x"]
    assert _uncontrolled_verdict_callers(fixture) == ["browser"]
    assert _uncontrolled_verdict_callers(called) == ["browser"], "⛔ the CALL spelling"
    assert _uncontrolled_verdict_callers(hook) == ["pytest_terminal_summary"]
    assert _uncontrolled_verdict_callers(helper) == ["test_x"], "⭐ reach, one level"
    assert _uncontrolled_verdict_callers(controlled) == []
    assert _uncontrolled_verdict_callers(helper_only) == [], "⛔ a HELPER cannot request one"
    assert _uncontrolled_verdict_callers(innocent) == []
    assert _uncontrolled_verdict_callers(direct) != _uncontrolled_verdict_callers(controlled)
    mine = Path(__file__).read_text(encoding="utf-8")
    assert "discovery.require_browser()" in mine, "⛔ the impossible reading needs its mention"
    assert _uncontrolled_verdict_callers(mine) == [], "⭐ a MENTION in a string is not a call"


def test_the_ENVIRONMENT_sweep_is_PLANTED_in_both_directions() -> None:
    """⭐ The other instrument, planted the same way — a name, a constant, and a silence."""
    literal = 'import os\ndef f():\n    return os.environ.get("STUDYFORGE_NEW", "")\n'
    constant = 'import os\nV = "STUDYFORGE_OTHER"\ndef f():\n    return os.environ[V]\n'
    unrelated = 'import os\ndef f():\n    return os.environ.get("HOME", "")\n'
    assert _reads_the_environment(literal, "m") == {"STUDYFORGE_NEW": "m.f"}
    assert _reads_the_environment(constant, "m") == {"STUDYFORGE_OTHER": "m.f"}
    assert _reads_the_environment(unrelated, "m") == {}, "⛔ only this project's own names"
    assert _reads_the_environment(literal, "m") != _reads_the_environment(unrelated, "m")


# --- the COUNT the declaration carries beside the verdict ---------------------


def test_the_count_of_what_DID_NOT_RUN_spans_every_outcome_that_reaches_no_verdict() -> None:
    """⛔ The same defect, arriving in the COUNT rather than in a test.

    ⭐ Browserless with `$STUDYFORGE_VISUAL` unset, the checks SKIP and the line
    says how many DID NOT RUN; with `=required` the same checks become fixture
    ERRORS, and a count of skips alone would read **`0`**. ⚠️ **A loudness mechanism
    that reads `0` when nothing ran reports the opposite of the truth.**

    ⭐ Asserted over a fixture rather than over a run, so it holds on a machine
    where every check passes.
    """

    class Report:
        def __init__(self, nodeid: str) -> None:
            self.nodeid = nodeid

    stats = {
        "skipped": [Report("tests/visual/test_capture.py::a"), Report("tests/other.py::x")],
        "error": [Report("tests/visual/test_site.py::b"), Report("tests/other.py::y")],
        "passed": [Report("tests/visual/test_init.py::c")],
    }
    assert conftest.checks_that_did_not_run(stats) == 2
    assert conftest.checks_that_did_not_run({"skipped": stats["skipped"]}) == 1
    assert conftest.checks_that_did_not_run({"error": stats["error"]}) == 1
    assert conftest.checks_that_did_not_run({}) == 0
    assert set(conftest.DID_NOT_RUN) == {"skipped", "error"}
