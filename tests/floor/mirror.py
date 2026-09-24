"""R12's mirror, enforced rather than remembered.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout, and depends on nothing outside it.

**What it does.** Fails any source module with no test module at the mirrored
path. `src/studyforge/serve/routes/content.py` requires
`tests/studyforge/serve/routes/test_content.py`, and a package's
`__init__.py` requires `test_init.py` beside its siblings. Only `src/` is
mirrored (`config.MIRRORS`).

**How you use it.** `check_mirrors(repo_root)` returns findings.
`mirror_for(relative_path)` answers "where does this module's test live" and
is the single definition of that mapping.

**Depends on.** `config.MIRRORS` and `pathlib`. Nothing imports the modules it
checks — the mapping is on names, so a module too broken to import is still
one whose missing test gets reported.

⚠️ Deliberately one-way. A test module with no source module is fine and
common: `tests/harness/`, `tests/visual/`, `tests/support.py`
and the repository-level tests all exist without a counterpart. Checking the
reverse direction would turn each of those into an exemption list that grows
every time somebody adds a legitimate test, which is how a check stops being
believed.

⚠️ A tree whose tests nest inside its own source root would read each test as
a source module wanting a test of its own, forever, so the first thing
`mirror_for` does is decline test files, wherever they sit.
"""

from __future__ import annotations

from pathlib import Path

from tests.floor import config
from tests.floor.report import Finding

RULE = "mirror"


def mirror_for(relative_path: str) -> str | None:
    """Where `relative_path`'s test must live, or None if it is not mirrored.

    Returns None for a path under no configured source root — `tests/` itself,
    for one, which is why running this over the whole tree is safe — and for
    any test file, including one that lives inside a source root.
    """
    if config.is_test_file(relative_path):
        return None
    for source_root, test_root in config.MIRRORS:
        prefix = source_root + "/"
        if not relative_path.startswith(prefix):
            continue
        within = relative_path[len(prefix) :]
        parent, _, name = within.rpartition("/")
        stem = Path(name).stem
        # A dunder module is tested like any other — `__init__.py` carries the
        # package contract (R17) and `__main__.py` carries the exit code — but
        # `test___init__.py` reads badly, so the underscores are dropped:
        # `test_init.py`, `test_main.py`.
        if stem.startswith("__") and stem.endswith("__"):
            stem = stem.strip("_")
        test_name = f"test_{stem}.py"
        segments = [test_root, parent, test_name] if parent else [test_root, test_name]
        return "/".join(segments)
    return None


def mirrored(root: Path) -> list[tuple[str, str]]:
    """Return `(module, the test it owes)` for every module R12 binds — this check's population.

    ⛔ One definition read by the check AND by `vacuity`'s disclosure, so
    the two can never describe different walks.
    """
    found: list[tuple[str, str]] = []
    for path in config.python_files(root):
        relative = config.relative(path, root)
        if config.is_test_file(relative):
            continue
        expected = mirror_for(relative)
        if expected is not None:
            found.append((relative, expected))
    return found


def check_mirrors(root: Path) -> list[Finding]:
    """Every source module whose mirrored test module is missing."""
    findings: list[Finding] = []
    for relative, expected in mirrored(root):
        if (root / expected).is_file():
            continue
        findings.append(
            Finding(
                path=relative,
                line=0,
                rule=RULE,
                message=(
                    f"no test module. Every module is tested, and the test tree mirrors "
                    f"the source tree — add `{expected}`."
                ),
            )
        )
    return findings
