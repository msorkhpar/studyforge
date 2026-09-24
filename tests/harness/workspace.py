r"""The workspace pin file, READ: which components this repository was built beside.

⭐ **The product suite's OWN reader of `workspace.json`**, copied from
`tools/workspace/` so a product test that reads a sibling at its pin needs no tooling. ⛔ It
READS and never verifies or records — `verify` and `record` are the tooling's commands and stay
there. Each copied definition is the original's byte for byte, and
`tests/test_process_twins.py` refuses a drift while both exist; this copy stays when the
tooling leaves.

**How you use it.** `read(repository_root)` returns the components, validated, or raises
`PinError` naming what is wrong. `workspace_root(repository)` is where the siblings sit;
`git` and `holds` ask a checkout one question each. `DEV_CONTAINER` names the variable the
pinned image sets. `tests.harness.pinned` reads one file out of a sibling at its pin.

**Depends on.** `git` on `PATH`, and the standard library.

## ⛔ The pin file contains no path, and that is the whole design

⭐ A component records a **name** and a **`where`** drawn from a closed set, and never a path:
a pin file's natural content is an absolute home path, which R7 forbids. `sibling` resolves to
`<workspace>/<name>` at run time; `self` is this repository.

## ⛔ The workspace root is computed, never recorded

⭐ The siblings sit beside the MAIN checkout: `git rev-parse --git-common-dir` names its `.git`,
whose grandparent is the workspace, so a linked worktree finds them too. ⚠️ Falling back to the
plain parent keeps this working in a plain copy with no git at all.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

#: The pin file's name, at the repository root.
PIN_FILENAME = "workspace.json"

#: The document's key order, which is the order it is written in (R10).
PIN_KEYS = ("workspace_api", "components")

#: Every key a component row may carry, in order (R10).
COMPONENT_KEYS = ("name", "where", "status", "commit")

#: The keys every row carries. ⚠️ `commit` is the one that comes and goes, and
#: `status` says exactly when — see `STATUS`.
REQUIRED_COMPONENT_KEYS = ("name", "where", "status")

#: ⛔ Whether a component exists yet, as a **closed set**. ⭐ The pin
#: file is the register, so *"this component is owed and does not exist"* has to
#: be sayable here — otherwise the owed half lives in a second file and E12 and
#: E13 have to remember it. ⚠️ A `not-yet-created` row flips to `present` in the
#: commit that creates the repository, and `verify` reds if it does not.
STATUS = ("present", "not-yet-created")

#: ⛔ A component's name is **one path component**, and the shape is closed.
#: ⭐ This is `where`'s own move carried the rest of the way: with `where`
#: closed and `name` free text in the same row, a name could hold `/etc`, or
#: `../../elsewhere`, or a home path — resolving outside the workspace and
#: getting echoed into a refusal. ⚠️ **Constrained, both are unrepresentable at
#: once**: there is no separator, no `..`, no leading dot, and nothing a
#: refusal would have to quote.
SAFE_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")

#: ⛔ Where a component sits, as a **closed set** — enumerability is a property
#: of the domain here, and a workspace has exactly two kinds of member. ⚠️ No
#: entry spells a path; `sibling` is resolved against the workspace root at run
#: time and `self` is this repository.
WHERE = ("self", "sibling")

#: 1 — the first shape. Bumped, never widened silently (R9).
WORKSPACE_API = 1

#: A commit as `git rev-parse` writes it.
SHA_LENGTH = 40


@dataclass(frozen=True, slots=True)
class Component:
    """One recorded component: what it is called, where it sits, what it was at."""

    name: str
    where: str
    status: str
    commit: str | None = None

    @property
    def present(self) -> bool:
        """Does this component exist yet? ⛔ `not-yet-created` is a first-class row."""
        return self.status == "present"

    def directory(self, workspace_root: Path, repository_root: Path) -> Path:
        """Resolve to a real directory — ⛔ computed here, never recorded.

        ⭐ Safe because `name` is one path component by contract: there is no
        separator to escape the workspace root with, and `SAFE_NAME` is what
        makes that true rather than a comment saying it should be.
        """
        return repository_root if self.where == "self" else workspace_root / self.name


class PinError(ValueError):
    """The pin file itself is unreadable or off contract."""


def read(repository_root: Path) -> tuple[Component, ...]:
    """Read and validate `workspace.json`, or raise naming what is wrong."""
    path = Path(repository_root) / PIN_FILENAME
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PinError(f"{PIN_FILENAME} is missing from the repository root") from None
    except json.JSONDecodeError as error:
        raise PinError(f"{PIN_FILENAME} is not valid JSON: {error.msg}") from None
    if not isinstance(document, dict) or tuple(document) != PIN_KEYS:
        raise PinError(f"{PIN_FILENAME} keys must be exactly {list(PIN_KEYS)}")
    if document["workspace_api"] != WORKSPACE_API:
        # ⛔ Names what is permitted; never reproduces what arrived (R7). The
        # value is corpus-shaped data out of a file, and the one shape being
        # refused is exactly the shape that carries a home directory.
        raise PinError(
            f"{PIN_FILENAME} must declare workspace_api {WORKSPACE_API}, "
            f"got {describe(document['workspace_api'])}"
        )
    return tuple(_component(row) for row in document["components"])


def _component(row: object) -> Component:
    """Read one row, refused rather than repaired.

    ⛔ **Nothing here reproduces a value.** Every refusal names the permitted
    shape instead, because a pin file is read from disk and the value being
    refused is the one most likely to be a path somebody's home directory is in.
    """
    if not isinstance(row, dict) or not _keys_in_order(tuple(row)):
        raise PinError(
            f"a component's keys must be {list(REQUIRED_COMPONENT_KEYS)}, "
            f"optionally then 'commit', in that order"
        )
    if not isinstance(row["name"], str) or not SAFE_NAME.match(row["name"]):
        # ⛔ The name is not quoted, which is the point: the refused shapes are
        # a path, a traversal and a home directory, and quoting one would copy
        # it into a build log from the check that exists to stop it.
        raise PinError(
            "a component's name must be a single path component: letters, "
            "digits, '.', '_' or '-', starting and ending alphanumeric"
        )
    if row["where"] not in WHERE:
        raise PinError(f"a component's 'where' must be one of {list(WHERE)}")
    if row["status"] not in STATUS:
        raise PinError(f"a component's 'status' must be one of {list(STATUS)}")
    return Component(name=row["name"], where=row["where"], **_commit(row))


def _keys_in_order(keys: tuple) -> bool:
    """Say whether these are the required keys, then `commit` if it is there at all."""
    return keys in (REQUIRED_COMPONENT_KEYS, COMPONENT_KEYS)


def _commit(row: dict) -> dict:
    """`commit` is present exactly when the component is (Ruling 54).

    ⛔ **Exactly**, in both directions. A `present` row with no commit pins
    nothing; a `not-yet-created` row with one claims a commit in a repository
    that does not exist, and a placeholder there would be the file pretending.
    """
    present = row["status"] == "present"
    if present and not _is_sha(row.get("commit")):
        raise PinError(
            f"{row['name']} is 'present', so it must record a full 40-character lowercase commit id"
        )
    if not present and "commit" in row:
        raise PinError(f"{row['name']} is not created yet, so it may not record a commit")
    return {"status": row["status"], "commit": row.get("commit")}


def describe(value: object) -> str:
    """Name what a value is, without reproducing what it says (R7).

    ⚠️ **Local, and not a call.** Ruling 31 keeps `tools/` from importing
    `studyforge`, so this is two lines of the same idea rather than a shared
    helper — and the alternative was echoing the value.

    ⭐ An `int` is quoted because an integer cannot carry a home directory, an
    address or a token; every other type is named, never shown.
    """
    if value is None:
        return "nothing"
    if isinstance(value, bool):
        return f"a {type(value).__name__}"
    if isinstance(value, int):
        return repr(value)
    name = type(value).__name__
    return f"{'an' if name[:1] in 'aeiou' else 'a'} {name}"


def _is_sha(value: object) -> bool:
    """Is this a full commit id? ⛔ Full, because an abbreviation can become ambiguous."""
    return (
        isinstance(value, str)
        and len(value) == SHA_LENGTH
        and all(c in "0123456789abcdef" for c in value)
    )


def git(directory: Path, *arguments: str) -> subprocess.CompletedProcess:
    """Run one git command in `directory`. ⛔ Never `--work-tree`, never a URL."""
    return subprocess.run(
        ["git", "-C", str(directory), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def holds(directory: Path, commit: str) -> bool:
    """Say whether this checkout holds that commit at all."""
    return git(directory, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


#: Set by `docker/dev/Dockerfile`. ⭐ Its presence means *"this run is the one
#: that certifies a result"* — the same marker the grammar tests read.
DEV_CONTAINER = "STUDYFORGE_DEV_CONTAINER"


def workspace_root(repository: Path) -> Path:
    """Return where the sibling components are: the parent of the **main** checkout."""
    result = git(repository, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if result.returncode == 0 and result.stdout.strip():
        common = Path(result.stdout.strip())
        if common.name == ".git" and common.parent.parent.is_dir():
            return common.parent.parent
    return repository.parent
