"""The repository's own acceptance: what it declares, and what it actually imports.

Not a mirror of any source module — it is about the tree as a whole, which is
why it sits at the top of `tests/` rather than under `tests/studyforge/`. The
size, mirror, contract and style floor is next door in
`tests/test_quality_floor.py`; what lives here is dependency policy, the
ignore rules, and the optional tooling.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from tests.harness import isolation
from tests.support import (
    git,
    init_repository,
    is_ignored,
    repository_root,
    run,
    tool_on_path,
    tracked_files,
)


def pyproject() -> dict:
    """`pyproject.toml`, parsed."""
    return tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))


# --- dependencies ----------------------------------------------------------


def test_no_runtime_dependencies():
    # ⛔ Standard library only in framework source. A runtime dependency is a
    # design change — it is also what would make R15's exemption for the
    # serving process stop being true, since a process with dependencies does
    # gain reproducibility from an image.
    assert pyproject()["project"]["dependencies"] == []


def test_optional_dependencies_are_tooling_only():
    extras = pyproject()["project"]["optional-dependencies"]
    assert set(extras) == {"test", "lint"}


def test_no_source_module_imports_a_third_party_package():
    # The declaration above says what is allowed; this says what is actually
    # imported, which is the half that goes wrong silently.
    #
    # ⛔ **Asked of `tests.harness.isolation`, not walked here.** The walk this
    # test used to carry and the one SF-26 needed for R1's import form are the
    # same eleven lines against the same closed set, and this file's neighbour
    # `tests/support.py` states the rule: a block repeated between test modules is
    # extracted and imported, because the copies drift silently while each keeps
    # passing. ⭐ The claim is unchanged and so is its strength — what moved is
    # where the predicate lives, and the harness is where it is proved to fail
    # when deliberately violated, which is the half this test never had.
    assert isolation.foreign_imports(isolation.framework_modules()) == []


def test_the_quality_tooling_is_excluded_from_packaging():
    # ⛔ `tools/` is developer tooling, not shipped API. Packaging looks only
    # in `src`, so an installed `studyforge` contains no `tools` package —
    # which is the other half of the ruling that kept the size checker out of
    # `src/studyforge/`.
    assert pyproject()["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]
    assert not (repository_root() / "src" / "tools").exists()


# --- ignore rules ----------------------------------------------------------

#: The shapes FND-04's golden fixtures will carry. ⚠️ None of them exists in
#: the tree yet, and that is the point: the risk is in what is not here to be
#: noticed. `site.json`, `*.unit.html` and `*.audio/` are all ignored
#: repository-wide, so without the `!tests/fixtures/**` negation these files
#: would be silently untracked — FND-04's suite passing on the machine that
#: wrote them and failing on every other checkout.
FIXTURE_SHAPES = (
    "tests/fixtures/depth1/.studyforge/site.json",
    "tests/fixtures/depth1/lesson-1.audio/s-1-abcd1234.mp3",
    "tests/fixtures/depth2/sib/page.unit.html",
)

#: The same three shapes anywhere else, where they ARE generated output and
#: must stay ignored.
GENERATED_SHAPES = (
    "corpora/depth1/.studyforge/site.json",
    "corpora/depth1/lesson-1.audio/s-1-abcd1234.mp3",
    "corpora/depth2/sib/page.unit.html",
)


def test_golden_fixtures_are_not_ignored():
    # ⛔ Load-bearing for another agent's committed work, and its failure is
    # silent. The negation works only because `!tests/fixtures/**` also
    # matches the intermediate directories — git normally cannot re-include a
    # file whose parent directory is excluded, and `.studyforge/` excludes one
    # of these parents. Narrowing the pattern to `**/*.json`, or moving it
    # above the rules it negates, breaks it with nothing failing loudly.
    swallowed = [path for path in FIXTURE_SHAPES if is_ignored(path)]
    assert swallowed == [], "golden fixtures would be silently untracked: " + ", ".join(swallowed)


def test_the_same_shapes_outside_the_fixtures_are_still_ignored():
    # ⚠️ Both directions, or the test above passes on a `.gitignore` that
    # ignores nothing at all — which is a worse state than the one it guards
    # against, and would look green.
    tracked = [path for path in GENERATED_SHAPES if not is_ignored(path)]
    assert tracked == [], "generated output is no longer ignored: " + ", ".join(tracked)


# --- optional tooling ------------------------------------------------------


#: ⛔ **`--force-exclude`, and it is load-bearing rather than decorative.**
#: `pyproject.toml` declares `extend-exclude = ["tests/fixtures"]`, and ruff
#: applies an exclusion to a file NAMED ON THE COMMAND LINE only when asked to.
#: ⚠️ Measured at `94ad941`: the tree tracks **no** `.py` under `tests/fixtures`,
#: so the flag changes nothing today — ⭐ which is exactly when a declared
#: exclusion is cheapest to keep. The first tracked fixture module would
#: otherwise be linted against a style an invalid fixture exists to violate.
SCOPED = ("--force-exclude", "--")


#: ⛔ **`ruff check`'s subject, and ONLY its subject.** ⚠️ MEASURED in the pinned
#: image: `ruff check` over the whole tracked set yields **9046 errors**, because
#: it reads a document AS Python. ⭐ Narrowing a committed verdict to what git
#: tracks is right; narrowing it to the wrong tracked THINGS is a second defect
#: of the same class, so each gate names its own population here.
LINT_POPULATION = ("*.py",)

#: ⛔ **`ruff format`'s subject is WIDER, and this is `CTO-64/1`.**
#: `pyproject.toml` sets `docstring-code-format = true`, so ruff 0.16.6 formats
#: the python blocks inside markdown as well as `.py` files — and **29 tracked
#: `.md` carry a python fence**, so the subject is live rather than theoretical.
#:
#: ⚠️ **MEASURED at `a04e590`, pinned image, three populations:** the disk form
#: `ruff format --check .` reports **876 files**; this population reports **876**;
#: `*.py` alone reports **532**. ⭐ **The disk form and the tracked form name the
#: SAME subjects** — so there is no trade-off here, and a `*.py`-only format gate
#: simply DROPS 344 files and goes blind to every python block in every document.
#:
#: ⛔ **Both arms were planted** (Ruling 191): a mis-formatted python block in a
#: tracked `.md` makes the disk form and this population exit `1` and the
#: `*.py`-only form exit `0` — it MISSES; mis-formatting a `.py` as well makes the
#: `*.py`-only form exit `1`, which is the control proving it is blind to
#: markdown specifically rather than blind in general.
FORMAT_POPULATION = ("*.py", "*.md")


def test_ruff_lint_is_clean_where_ruff_exists():
    # ⚠️ Ruff is not installed in the environment this was built in and no
    # network install is assumed, so this skips with a message that names the
    # extra rather than passing quietly. Where ruff is present — FND-03's
    # image is the obvious place — it runs for real.
    #
    # ⛔ **Over what git TRACKS, never `.`** (`W142`, and Ruling 80's own clause —
    # *a floor check's verdict may not depend on untracked state*). `ruff check .`
    # walks the DISK, so an untracked scratch module at the repository root turns
    # a CORRECT tree red: measured by two offices, and it failed three innocent
    # branches in one wave under a reviewer who had measured it that same hour.
    #
    # ⚠️ **The working-tree reading is not deleted, it is demoted** (Ruling 183's
    # standing form): `tools/quality/lint.py`'s NOTICE still walks the disk, still
    # names the scratch file's findings, and by Rulings 77 and 78 can never fail a
    # build. ⭐ A reviewer still learns their scratch file is dirty — as a notice,
    # and not as three branches failing.
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    result = run([ruff, "check", *SCOPED, *tracked_files(LINT_POPULATION)], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr


def test_ruff_format_is_clean_where_ruff_exists():
    # ⛔ **`FORMAT_POPULATION`, not `LINT_POPULATION`** — see that constant for the
    # measurement. The two gates ask different questions and take different
    # subjects; sharing one population is how the wider gate silently narrows.
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    result = run(
        [ruff, "format", "--check", *SCOPED, *tracked_files(FORMAT_POPULATION)],
        cwd=repository_root(),
    )
    assert result.returncode == 0, result.stdout + result.stderr


def declared_target() -> str:
    """The formatter target `requires-python` implies, as ruff spells it (`py314`).

    ⛔ Only a `>=3.N` floor is understood. Any other shape fails rather than guesses,
    because a changed `requires-python` is a changed target that somebody must choose.
    """
    requires = pyproject()["project"]["requires-python"]
    match = re.fullmatch(r">=3\.(\d+)", requires)
    assert match, f"requires-python {requires!r} is not a `>=3.N` floor; choose a target by hand"
    return f"py3{match.group(1)}"


def test_the_formatter_target_is_declared_once_and_follows_requires_python():
    # ⛔ `W116`, Ruling 210. Deleting the declaration leaves every ruff gate GREEN,
    # because ruff then INFERS the same target from `requires-python` — so the
    # inference is invisible to the format gate, and this is the check that sees it.
    ruff_table = pyproject()["tool"]["ruff"]
    assert ruff_table.get("target-version") == declared_target(), (
        "[tool.ruff] target-version must be declared and equal requires-python's floor"
    )
    # ⚠️ A per-file override is a second target held more quietly (`W196`, refusal 2).
    assert "per-file-target-version" not in ruff_table


def test_every_formatted_directory_resolves_the_declared_target():
    # ⛔ `W116`: the declaration counts only if every formatter run READS it. A
    # `ruff.toml` or `.ruff.toml` anywhere on disk wins over `pyproject.toml` for its
    # subtree, even untracked, so ruff itself is asked, once per directory the format
    # gate formats. ⭐ Failures name the directory only, never ruff's absolute
    # settings path (R7).
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    root = repository_root()
    excluded = tuple(f"{prefix}/" for prefix in pyproject()["tool"]["ruff"]["extend-exclude"])
    first_in_directory: dict[str, str] = {}
    for name in tracked_files(FORMAT_POPULATION):
        if not name.startswith(excluded):
            first_in_directory.setdefault(name.rpartition("/")[0] or ".", name)
    assert first_in_directory, "no formatted directory to probe"
    version = declared_target().removeprefix("py")
    wanted = {
        "formatter.unresolved_target_version": f"{version[0]}.{version[1:]}",
        "linter.unresolved_target_version": f"{version[0]}.{version[1:]}",
        "formatter.per_file_target_version": "{}",
        "linter.per_file_target_version": "{}",
    }
    wrong = []
    for directory, probe in sorted(first_in_directory.items()):
        shown = run([ruff, "check", "--show-settings", "--", probe], cwd=root)
        settings = dict(
            line.strip().split(" = ", 1)
            for line in shown.stdout.splitlines()
            if line.strip().split(" = ", 1)[0] in wanted
        )
        path = re.search(r'^Settings path: "(.*)"$', shown.stdout, re.MULTILINE)
        if (
            shown.returncode != 0
            or settings != wanted
            or path is None
            or Path(path.group(1)).resolve() != (root / "pyproject.toml").resolve()
        ):
            wrong.append(directory)
    assert wrong == [], (
        f"{len(wrong)} of {len(first_in_directory)} formatted directories do not resolve "
        f"[tool.ruff] target-version from pyproject.toml: {wrong}"
    )


def test_the_format_population_covers_python_blocks_in_documents(tmp_path):
    # ⛔ **`CTO-64/1`, made permanent** (R12). The measurement that produced
    # `FORMAT_POPULATION` lives in a reviewer's terminal and in a constant's
    # comment; this is the part that goes red if someone narrows the gate again.
    #
    # ⭐ **It asserts the CAUSE and the EFFECT, in that order.** The cause is this
    # repository's own declaration — without `docstring-code-format` the wider
    # population would be pointless — and the effect is measured with the real
    # tool in a throwaway repository that declares the same thing.
    assert pyproject()["tool"]["ruff"]["format"]["docstring-code-format"] is True
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    repository = init_repository(tmp_path / "repository")
    (repository / "pyproject.toml").write_text(
        "[tool.ruff.format]\ndocstring-code-format = true\n", encoding="utf-8"
    )
    (repository / "clean.py").write_text("VALUE = 1\n", encoding="utf-8")
    # A python block a formatter would rewrite, inside a document.
    (repository / "doc.md").write_text("```python\nx=1\n```\n", encoding="utf-8")
    assert (
        run([git(), "add", "pyproject.toml", "clean.py", "doc.md"], cwd=repository).returncode == 0
    )

    narrow = run(
        [ruff, "format", "--check", *SCOPED, *tracked_files(LINT_POPULATION, repository)],
        cwd=repository,
    )
    assert narrow.returncode == 0, (
        "the *.py-only population stopped being blind to markdown, so this test "
        "no longer inhabits the defect it exists to refuse"
    )
    wide = run(
        [ruff, "format", "--check", *SCOPED, *tracked_files(FORMAT_POPULATION, repository)],
        cwd=repository,
    )
    assert wide.returncode == 1, (
        "the format population no longer sees a python block in a document: " + wide.stdout
    )


def test_the_lint_verdict_is_taken_over_tracked_content_in_both_directions(tmp_path):
    # ⛔ **R12's both directions, and both arms are INHABITED** (Ruling 191).
    # The plant lives in a throwaway repository rather than in this one: a
    # control that can only be written by writing into the tree it measures is
    # not a control (Ruling 11).
    #
    # ⚠️ **The middle assertion is the one that keeps this honest.** It runs the
    # disk-walking form in the same directory and requires it to go RED — so the
    # defect stays inhabited by the very shape this test replaces, and the day
    # ruff changes that behaviour this test says so instead of quietly passing.
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    repository = init_repository(tmp_path / "repository")
    (repository / "tracked.py").write_text("VALUE = 1\n", encoding="utf-8")
    assert run([git(), "add", "tracked.py"], cwd=repository).returncode == 0
    # An untracked, un-ignored, lint-dirty module — the exact shape found by
    # accident in one checkout and planted deliberately in another.
    (repository / "scratch_probe.py").write_text("import json\n", encoding="utf-8")

    assert tracked_files(LINT_POPULATION, repository) == ["tracked.py"], (
        "the plant is not untracked"
    )
    verdict = run(
        [ruff, "check", *SCOPED, *tracked_files(LINT_POPULATION, repository)], cwd=repository
    )
    assert verdict.returncode == 0, (
        "an UNTRACKED lint-dirty module turned the committed verdict red: " + verdict.stdout
    )
    assert run([ruff, "check", "."], cwd=repository).returncode == 1, (
        "the disk-walking form no longer goes red here, so this test has stopped "
        "inhabiting the defect it exists to refuse"
    )

    assert run([git(), "add", "scratch_probe.py"], cwd=repository).returncode == 0
    assert sorted(tracked_files(LINT_POPULATION, repository)) == ["scratch_probe.py", "tracked.py"]
    now_tracked = run(
        [ruff, "check", *SCOPED, *tracked_files(LINT_POPULATION, repository)], cwd=repository
    )
    assert now_tracked.returncode == 1, (
        "a TRACKED lint-dirty module did not turn the committed verdict red"
    )
