"""Every number and path the quality floor enforces, in one place.

**What it does.** Holds the ceilings, the markers and the tree layout that the
four checks share, so a rule is stated once rather than re-typed in four
modules that then drift apart.

**How you use it.** Import the constant; never re-declare it. `python_files()`,
`is_test_file()` and `ceiling_for()` answer the questions every check asks
about a path.

**Depends on.** `pathlib`, `re`, `shutil` and `subprocess` — all standard
library — and `report`, for the shape a walk's answer takes (`W148`). ⚠️ This
line read *"`pathlib` only"* while the module had imported `shutil` and
`subprocess` since `FND-08`; corrected here because `W45` was editing it
anyway, and R17's third part is worth nothing if it is decorative.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from tools.quality.report import DISK_WALK, TRACKED_WALK, DocumentPopulation

# --- R11: the size ceiling -------------------------------------------------

#: Physical lines, counted as `wc -l` counts them: `len(text.splitlines())`.
#: Physical and not logical, because the number has to be checkable by hand
#: from a shell before anybody trusts the tool that reports it.
SOURCE_LINE_CEILING = 400
TEST_LINE_CEILING = 600

#: The per-module opt-out. A module over its ceiling passes only if its own
#: module docstring — the FIRST docstring in the file — carries a line
#: beginning with this marker, followed by a real reason.
#:
#: ⛔ The literal string is fixed and case-sensitive, by ruling: the review
#: rubric greps for exactly this token, so a marker that differs by a hyphen
#: or a capital passes the checker and then fails review, which is the worst
#: of the available outcomes. Matched via `ast`, never anywhere in the file: a
#: comment next to the offending code is not a contract, and a string in the
#: middle of a function is not something a reader of the module's top will
#: ever see.
SIZE_EXCEPTION_MARKER = "Size exception:"

#: Minimum characters of justification after the marker. Not a quality bar —
#: it only stops `Size exception: yes` from being a way through the gate.
#:
#: ⚠️ Measured against the WHOLE justification, not the marker line. Measuring
#: one line refused a long, correct, multi-line reason for being short
#: (Ruling 114).
MIN_JUSTIFICATION_CHARS = 20

#: How a deferral is told apart from a design claim: its reason names a board
#: row (review rubric 3c, Ruling 113). Two id shapes are in use — `SF-35`,
#: `FND-01`, `OPS-05` (an epic prefix, a number, an optional letter suffix)
#: and `W44` (the wave rows, which carry no hyphen).
#:
#: ⛔ Deliberately narrow, and the narrowness is the point. `R11` is a rule,
#: `M2` a milestone, `C5` a constraint and `E08` an epic — none of them a row
#: anybody can close, and a design claim has to stay free to cite them without
#: being read as a deferral. Only `W` takes the hyphenless form.
#:
#: ⚠️ It answers *"is a row named here"*, never *"is that row live"*. Whether
#: the id is a row still open is the wave-open sweep's question and a
#: reviewer's, because this package may not read the board (it would be
#: checking a document that changes hourly against a tree that does not).
ROW_ID = re.compile(r"\b(?:[A-Z]{2,4}-[0-9]{1,3}[a-z]?|W[0-9]{1,3})\b")

# --- R17: contracts --------------------------------------------------------

#: Minimum characters of module docstring under `src/` and `tools/`. Presence
#: and substance are machine-checkable; R17's three parts (what it does, how
#: you use it, what it depends on) are a review criterion, because a checker
#: that parsed for three headings would be enforcing a template nobody agreed
#: to and would pass a module that filled it in with nothing.
MIN_DOCSTRING_CHARS = 40

# --- style -----------------------------------------------------------------

#: ⛔ Must equal `[tool.ruff] line-length` in `pyproject.toml`.
#: `tools/tests/quality/test_config.py` asserts it.
LINE_LENGTH = 100

# --- the tree --------------------------------------------------------------

#: Directories the checks read, relative to the repository root.
SCAN_ROOTS = ("src", "tools", "tests")

#: Directories whose Python files are held to the test ceiling. Two, because
#: the tooling's tests sit beside the tooling (see `MIRRORS`).
TEST_ROOTS = ("tests", "tools/tests")

#: R12's mirrors: (source directory, test directory). A source module
#: `<source>/a/b.py` must have a test at `<test>/a/test_b.py`.
#:
#: ⚠️ There are two pairs, not one, and the second is the ruled shape. The
#: framework's tests mirror `src/` into the one `tests/` tree. The tooling's
#: tests sit **beside the tooling**, at `tools/tests/`, because R12's
#: requirement is locality of tests rather than one global tree — and because
#: `tools/` is not shipped API and has no business appearing in the tree that
#: mirrors what is. Either way the mapping is the same mapping, computed once
#: in `mirror.mirror_for`.
MIRRORS = (
    ("src/studyforge", "tests/studyforge"),
    ("tools", "tools/tests"),
)

#: Nothing a person wrote lives in these — they are build output, tool caches
#: and version-control internals. ⛔ No check reads them, ever, including the
#: personal-data sweep: `.git` holds every previous version of every file, so
#: sweeping it would report a violation that was already corrected as if it
#: were current.
TOOL_OUTPUT_DIRS = (
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "graphify-out",
    "node_modules",
)

#: Never read by the *style, size, mirror and contract* checks. `tests/fixtures/`
#: is FND-04's, and a fixture is deliberately shaped wrong — an invalid corpus is
#: its whole purpose — so holding it to the repository's style is a category
#: error.
#:
#: ⚠️ The personal-data sweep does NOT use this list, and the difference is the
#: point: a fixture may be badly formatted on purpose, but the one place this
#: repository is allowed to hold a personal-data shape is a single named
#: directory (`SANCTIONED_PERSONAL_DATA_DIRS`), not the whole fixture tree. A
#: sweep that skipped `tests/` wholesale would have stopped checking exactly
#: where such data lives.
EXCLUDED_DIRS = ("tests/fixtures", *TOOL_OUTPUT_DIRS)

#: ⛔ The complete list of directories permitted to contain personal-data
#: **shapes**, and the rule each is the negative fixture for. Rubric §1e: the
#: exception exists because a gate that refuses such data needs an input to
#: refuse, and it is bounded by tests rather than by a reviewer's memory.
#:
#: Every value inside one of these is fabricated and unreachable — an RFC 2606
#: reserved TLD, a documented placeholder home path — and each directory says
#: so in a `VIOLATION.md` beside the data. Adding an entry here is how a sixth
#: negative fixture becomes legal, and `tools/tests/quality/test_personal_data.py`
#: fails if one appears without it.
SANCTIONED_PERSONAL_DATA_DIRS = ("tests/fixtures/invalid/personal-data",)


#: Test modules that are shared machinery rather than a mirror of a source
#: module. They are still size- and style-checked; they are simply not
#: expected to correspond to anything under `src/`.
TEST_SUPPORT_NAMES = ("conftest.py", "support.py")


def is_excluded(relative_path: str) -> bool:
    """Report whether `relative_path` (repo-relative, forward slashes) is read."""
    parts = relative_path.split("/")
    return any(
        excluded in parts or relative_path.startswith(excluded + "/") for excluded in EXCLUDED_DIRS
    )


def is_sanctioned_personal_data(relative_path: str) -> bool:
    """Report whether the path sits inside a registered negative-fixture directory."""
    return any(
        relative_path == directory or relative_path.startswith(directory + "/")
        for directory in SANCTIONED_PERSONAL_DATA_DIRS
    )


def is_tool_output(relative_path: str) -> bool:
    """Report whether the path is build output, a tool cache or `.git`."""
    parts = relative_path.split("/")
    return any(
        directory in parts or relative_path.startswith(directory + "/")
        for directory in TOOL_OUTPUT_DIRS
    )


def is_test_file(relative_path: str) -> bool:
    """Report whether the file is held to `TEST_LINE_CEILING`, not the source one."""
    return any(relative_path == root or relative_path.startswith(root + "/") for root in TEST_ROOTS)


def ceiling_for(relative_path: str) -> int:
    """Return the line ceiling that applies to `relative_path`."""
    return TEST_LINE_CEILING if is_test_file(relative_path) else SOURCE_LINE_CEILING


def relative(path: Path, root: Path) -> str:
    """`path` as a repo-relative string with forward slashes, for reporting.

    ⛔ Repo-relative and never absolute: an absolute path here carries the
    user's home directory into a build log, which is personal data (R7).
    """
    return path.relative_to(root).as_posix()


def ignored_paths(root: Path, candidates: list[Path]) -> set[Path]:
    """Return which of `candidates` git would ignore, in one call.

    ⛔ One subprocess for the whole tree, never one per file: `git check-ignore
    --stdin` takes the list and answers it in a batch, and the alternative is
    a hundred process launches on every run of the floor.

    Returns an **empty set** whenever git cannot answer — not installed, or
    `root` is not a repository, which is the normal case for a test's
    temporary tree. ⚠️ That fails *open*: an unanswerable question means
    everything is swept, which reports too much rather than too little. The
    other direction would silently stop checking.
    """
    git = shutil.which("git")
    if git is None or not candidates:
        return set()
    payload = "\0".join(relative(path, root) for path in candidates)
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "check-ignore", "--stdin", "-z"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            timeout=30,
        )
    except OSError, subprocess.SubprocessError:
        return set()
    if result.returncode not in (0, 1):  # 128: not a repository, or worse
        return set()
    return {root / name for name in result.stdout.split("\0") if name}


def text_files(root: Path) -> list[Path]:
    """Every readable text file the repository is responsible for, sorted.

    ⚠️ Wider than `python_files` on purpose. A home directory reaching disk
    does not care what extension the file has: R7 has been violated in this
    repository once already and it was in a **document**, so this walks the
    whole tree rather than three roots of `.py`. Anything that will not decode
    as UTF-8 is skipped — a PNG has no strings to sweep.

    ⛔ **But a git-ignored path is not the repository's, and is not read.**
    `.idea/workspace.xml` legitimately carries the paths of whoever has the
    project open; it is ignored, it has not entered the repository and it
    never will. Gating on it makes the floor unconditionally red for anyone
    with an IDE running — and a floor that is red for a reason nobody can fix
    is one people learn to run through a filter, after which it is not read at
    all.

    ⭐ **Ignored, not untracked, and the difference is the whole point.** A
    file you have just written and not yet added is exactly what a gate on
    "personal data entering the repository" must catch — *before* it enters,
    not in the commit that carries it. `git ls-files` would miss it. So the
    rule is: everything except what git has been told to ignore.

    Sorted, for the same reason as `python_files`: two machines must produce
    the same findings in the same order.
    """
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        # ⛔ `.git` itself is NOT "ignored" as far as git is concerned — it is
        # simply not part of the worktree — so this pre-filter is doing real
        # work rather than duplicating the call below.
        if is_tool_output(relative(path, root)):
            continue
        candidates.append(path)
    ignored = ignored_paths(root, candidates)
    return sorted(path for path in candidates if path not in ignored)


def tracked_paths(root: Path) -> set[Path] | None:
    """Return the paths git's INDEX holds under `root`, or None when it cannot say.

    ⛔ **`None` is a THIRD answer and is never an empty set** (Ruling 216). A
    tree with no git, or one that is not a repository — the normal case for a
    test's temporary directory — has not said it tracks *nothing*; it has
    failed to answer, and coercing that to `set()` empties every population
    built on it in silence.

    ⚠️ **The INDEX, and `ignored_paths` asks a DIFFERENT question on purpose.**
    That one answers *has this repository been told to ignore this*, which the
    personal-data sweep needs: a file written and not yet added must be swept
    **before** it enters. This answers *is this file repository state*, which
    is what a figure quoted between two checkouts needs.
    """
    git = shutil.which("git")
    if git is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "ls-files", "-z"],
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            timeout=30,
        )
    except OSError, subprocess.SubprocessError:
        return None
    if result.returncode != 0:  # 128: not a repository, or worse
        return None
    return {root / name for name in result.stdout.split("\0") if name}


def markdown_population(root: Path) -> DocumentPopulation:
    """Every markdown document git TRACKS under `root`, sorted, with its walk.

    ⭐ **A narrowing of `text_files`, never a second walk.** FND-08's acceptance
    forbids a second file-walking helper: the pointer check needs *documents*
    rather than *every text file*, and that is one `suffix` test away from the
    walk `check_personal_data` already runs. Exclusions, git-ignore and the
    sort order are therefore inherited rather than restated, and a directory
    added to `TOOL_OUTPUT_DIRS` reaches this walk on the same commit.

    ⛔ **And one further narrowing, which is `W148`: the document population is
    repository state, and repository state is what git TRACKS.** An untracked
    markdown file in a main checkout is counted by a disk walk and is absent
    from every linked worktree, so no disk-derived figure is reproducible
    between two correct checkouts at ONE ref — measured, `458` against `457`,
    same content, ZERO extra pointers, which defeats Ruling 277's ROLE
    discipline exactly where it is supposed to work.

    ⛔ **THE NARROWING IS HERE AND NEVER IN `text_files`.** That walk is the
    personal-data sweep's population and its own docstring says why it is
    ignore-based: narrowing *it* to the index would take every not-yet-added
    file out of the R7 gate — the one thing that gate exists to catch.

    ⚠️ **`tests/fixtures/` is IN, by decision and not by accident.** It is in
    `EXCLUDED_DIRS`, so a `python_files`-shaped walk would not see it — but
    this walk is `text_files`-shaped and `EXCLUDED_DIRS` never applied to it.
    ⭐ The decision matches the personal-data sweep's, for the same reason: a
    fixture is allowed to be *shaped* wrong — an invalid corpus is its whole
    purpose — but `tests/fixtures/README.md` is prose a person reads, and a
    pointer that goes nowhere is broken there exactly as it is in `docs/`.
    ⛔ Measured before deciding, on `2926dc2`: 8 markdown files under
    `tests/fixtures/` carrying **0 pointers between them**, so including them
    costs no migration today and closes the hole before one is written.
    """
    documents = [path for path in text_files(root) if path.suffix == ".md"]
    tracked = tracked_paths(root)
    if tracked is None:
        return DocumentPopulation(tuple(documents), DISK_WALK)
    return DocumentPopulation(tuple(path for path in documents if path in tracked), TRACKED_WALK)


def markdown_files(root: Path) -> list[Path]:
    """Return the paths half of `markdown_population`.

    ⛔ A caller that prints a FIGURE takes the population instead, so the walk
    that produced its denominator is printed beside it (`W148`).
    """
    return list(markdown_population(root).paths)


def read_text(path: Path) -> str | None:
    """Return the file's text, or None when it is not text at all."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError, OSError:
        return None


def python_files(root: Path) -> list[Path]:
    """Every non-excluded `.py` file under the scan roots, sorted.

    Sorted rather than in filesystem order, because R10's reproducibility
    argument applies to a report as much as to a page: two machines must
    produce the same list of findings in the same order.
    """
    found: list[Path] = []
    for scan_root in SCAN_ROOTS:
        directory = root / scan_root
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.py"):
            if path.is_file() and not is_excluded(relative(path, root)):
                found.append(path)
    return sorted(found)
