r"""The library this Python imports: its version, and whether a corpus's pin names it.

**What it does.** Reads the version of the `studyforge` that is actually
loaded — from the distribution metadata an installed wheel puts beside the
package, or from the `pyproject.toml` of the source tree it was loaded from —
and compares it with the version an onboarded corpus's pin records.

**How you use it.** `version()` is the loaded library's version, and
`pinned(root)` is the pin a corpus records, refused by name when it predates
version pins. From a shell, `verify` is the command that compares the two.

**Depends on.** `tomllib` and `pathlib` from the standard library, `archive.scrub`
for the personal-data gate on the pin it reads back, and this package's `pin`
for where the pin lives and the shapes of what it records. ⛔ Not `importlib`
in any form: a framework module never reaches a module by name at run time
(R1, `tests/harness/test_isolation.py`), so the metadata is read from the
directory the package was loaded from — the rule `studyforge.skills.documents`
keeps too.

## ⛔ The INSTALLED library, never a checkout beside the corpus

⚠️ **A stranger converting their own material has no sibling checkout of the
framework**: they install the library. ⭐ **So the version is read from what this
Python imports** — ⛔ never from a path a corpus reaches, and never written
down: a path here is this machine's, at run time (R7).

⭐ **Two places, in this order, and nothing is guessed.** An installed wheel puts
`studyforge-<version>.dist-info/METADATA` beside the package; a source tree has
`pyproject.toml` two levels above it (the `src/` layout), which is also what an
editable install loads. ⛔ Neither found, or two distributions beside one
package, is refused by name: a version this module cannot state is not one a
pin may record.

## ⭐ The commit, as the wheel was stamped with it

⚠️ A wheel carries no git history, so its commit cannot be read from a
checkout. ⭐ **A wheel carries `STAMP`** instead, the
commit the build ran at (the repository's `setup.py` writes it), so `commit()`
reads it beside the package, `onboard` pins it without being told, and the
corpus's generated `test_framework_pin.py` checks it. ⚠️ **A source tree or an
editable install has no stamp and answers `None`**: its commit is whatever the
checkout holds, and this module reads no checkout. Onboarding from one takes
the commit from its caller, and the generated check says it cannot
verify it rather than passing.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.skills.onboarding.pin import (
    FRAMEWORK,
    PIN_API,
    PIN_FILE,
    WHERE,
    PinRefused,
    check_commit,
    check_version,
)
from studyforge.version import check as check_contract

#: The `studyforge` package directory this module was loaded from.
PACKAGE = Path(__file__).resolve().parents[2]

#: The file a built wheel carries its commit in, inside the package.
STAMP = "COMMIT"


class LibraryRefused(LookupError):
    """The loaded library's version cannot be read, and why — naming no path (R7)."""


def version(package: Path = PACKAGE) -> str:
    """Return the version of the `studyforge` loaded from `package`, or refuse by name."""
    found = [_metadata(entry) for entry in sorted(package.parent.glob(f"{FRAMEWORK}-*.dist-info"))]
    named = [value for value in found if value is not None]
    if len(named) > 1:
        raise LibraryRefused(
            f"{len(named)} {FRAMEWORK} distributions are installed beside the one package "
            f"this Python imports, so which version it is cannot be said; uninstall all but one"
        )
    declared = named[0] if named else _source_tree(package)
    if declared is not None:
        try:
            return check_version(declared)
        except PinRefused as error:
            raise LibraryRefused(str(error)) from None
    raise LibraryRefused(
        f"the {FRAMEWORK} this Python imports has neither installed distribution metadata "
        f"beside it nor a pyproject.toml above it, so its version cannot be read; install "
        f"the library (a wheel built from the framework) into this Python"
    )


def commit(package: Path = PACKAGE) -> str | None:
    """Return the commit the loaded library was built from, `None` for an unbuilt tree.

    ⛔ A stamp that is not a commit is refused, never quoted (R7).
    """
    try:
        text = (package / STAMP).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError, ValueError:
        raise LibraryRefused(
            f"the {FRAMEWORK} this Python imports carries an unreadable "
            f"{STAMP}; install a wheel built from a clone"
        ) from None
    try:
        return check_commit(text.strip())
    except PinRefused as error:
        raise LibraryRefused(f"{STAMP}: {error}") from None


def built_from(asked: str | None) -> str:
    """Return the commit a pin records: the library's own, or the caller's when it has none.

    ⛔ A commit the caller names that is not the one the library was built from is
    refused by name: the pin would name a library this Python does not import.
    """
    known = commit()
    if asked is None and known is None:
        raise LibraryRefused(
            f"the {FRAMEWORK} this Python imports is a source tree, not a built wheel, so "
            f"it cannot say which commit it is; pass framework_commit=<the checkout's commit>"
        )
    if asked is None:
        return known
    check_commit(asked)
    if known is not None and asked != known:
        raise LibraryRefused(
            f"framework_commit names another commit than the one the {FRAMEWORK} this Python "
            f"imports was built from; leave it out and the library's own is pinned, or "
            f"install the library built from the commit you named"
        )
    return asked


def _metadata(dist_info: Path) -> str | None:
    """Return the `Version:` of one dist-info whose `Name:` is this library, else `None`."""
    try:
        text = (dist_info / "METADATA").read_text(encoding="utf-8")
    except OSError, ValueError:
        return None
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            break  # ⭐ The headers end at the first blank line; the rest is the readme.
        key, _, value = line.partition(":")
        fields.setdefault(key.strip().lower(), value.strip())
    if fields.get("name", "").lower().replace("_", "-") != FRAMEWORK:
        return None
    return fields.get("version")


def _source_tree(package: Path) -> str | None:
    """Return the version a `src/`-layout source tree declares for this library, else `None`."""
    if package.parent.name != "src":
        return None
    try:
        with (package.parent.parent / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle).get("project", {})
    except OSError, ValueError:
        return None
    if not isinstance(project, dict) or project.get("name") != FRAMEWORK:
        return None
    declared = project.get("version")
    return declared if isinstance(declared, str) else None


def pinned(root: Path | str) -> dict:
    """Return the pin at `root`, gated (R7). ⛔ A pin with no `version` predates version pins."""
    where = Path(root) / PIN_FILE
    try:
        document = json.loads(where.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise LibraryRefused(f"{PIN_FILE} is not here or is not JSON, so there is no pin") from None
    assert_clean(document, PIN_FILE)
    if not isinstance(document, dict) or document.get("where") != WHERE:
        raise LibraryRefused(
            f"{PIN_FILE} predates the installed library: it names a framework checkout "
            f"beside this corpus, not an installed version. Re-onboard it from the "
            f"installed library, re-pinning: reonboard('.', framework_commit=<the commit "
            f"the library was built from>).write('.', regenerate=True)"
        )
    check_contract(
        "pin_api", document.get("pin_api"), (PIN_API,), where=PIN_FILE, error=LibraryRefused
    )
    try:
        return {
            **document,
            "version": check_version(document.get("version")),
            "commit": check_commit(document.get("commit")),
        }
    except PinRefused as error:
        raise LibraryRefused(f"{PIN_FILE}: {error}") from None
