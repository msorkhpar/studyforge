"""Every number and path the quality floor enforces, in one place.

**What it does.** Holds the ceilings, the markers and the tree layout that the
four checks share, so a rule is stated once rather than re-typed in four
modules that then drift apart.

**How you use it.** Import the constant; never re-declare it. `python_files()`,
`is_test_file()` and `ceiling_for()` answer the questions every check asks
about a path.

**Depends on.** `pathlib` only.
"""

from __future__ import annotations

from pathlib import Path

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
MIN_JUSTIFICATION_CHARS = 20

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


def text_files(root: Path) -> list[Path]:
    """Every readable text file in the tree, sorted — not just the Python ones.

    ⚠️ Wider than `python_files` on purpose. A home directory reaching disk
    does not care what extension the file has: R7 has been violated in this
    repository once already and it was in a **document**. So this walks the
    whole tree from the root, skipping only tool output, and skipping any file
    that will not decode as UTF-8 — a PNG has no strings to sweep and reading
    one as text is meaningless rather than merely useless.

    Sorted, for the same reason as `python_files`: two machines must produce
    the same findings in the same order.
    """
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if is_tool_output(relative(path, root)):
            continue
        found.append(path)
    return sorted(found)


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
