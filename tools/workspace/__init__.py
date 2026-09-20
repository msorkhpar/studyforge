r"""The workspace pin file: which components this repository was built beside.

**What it does.** Reads `workspace.json`, resolves each component to a
directory beside this one, and answers whether the checkouts on disk are the
ones the file records — in **both** directions.

**How you use it.** `verify(workspace_root)` returns findings, empty when
correct. `record(workspace_root)` returns the document to write.

**Depends on.** `git` on `PATH`, and the standard library.

## ⛔ Why this is a pin file and not a submodule

R18 was amended by a standing decision: **nothing is ever pushed to any
remote.** ⭐ A submodule is exactly two things — a URL and a commit — and only
the URL half needed pushing, so the commit half is kept here and verified
against the local checkouts.

⛔ **All three submodule forms are closed, and the third settles it:**

| form | why it fails |
|---|---|
| an absolute local path | ⛔ a home directory in a tracked file (R7) |
| a relative URL | resolves against a parent remote that will not exist |
| a real remote | names a commit nobody pushed — ⛔ so it resolves to nothing **including here** |

## ⛔ The pin file contains no path, and that is the whole design

⚠️ **A pin file's natural content is "where each component lives", and that is
an absolute home path** — the one thing this project forbids most absolutely,
and one it has already violated once in its own documents.

⭐ So a component records a **name** and a **`where`** drawn from a closed set,
and never a path. `sibling` resolves to `<workspace>/<name>` at run time;
`self` is this repository. The file has no `/`, no `..`, and nothing about the
machine it was written on. ⚠️ Same argument as W8's: a program on `PATH` is a
fact about the environment, and `/usr/bin/mvn` is a fact about one laptop.

## ⛔ What R18 kept, and what it gave up

- ⭐ **Kept: reproducible across time on this machine.** That is what R9's
  cross-repository versioning needs, and it was the half doing the work.
- ⛔ **Given up: reproducible across machines.** ⚠️ **A real reduction, not a
  restatement.** If pushing is ever adopted, the recorded commits are exactly
  what a submodule would have wanted — so it is recoverable, and it is not
  currently held.

## ⚠️ `studyforge`'s own row cannot be checked for equality

A file inside this repository cannot contain the hash of the commit that
contains it: recording it changes `HEAD`, which changes the hash. ⛔ So the
`self` row is verified as **present locally and an ancestor of `HEAD`**, which
is the strongest true statement available, and equality is *unrepresentable*
rather than merely unchecked.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.workspace.checkout import uncommitted

#: The pin file's name, at the repository root.
PIN_FILENAME = "workspace.json"

#: The document's key order, which is the order it is written in (R10).
PIN_KEYS = ("workspace_api", "components")

#: Every key a component row may carry, in order (R10).
COMPONENT_KEYS = ("name", "where", "status", "commit")

#: The keys every row carries. ⚠️ `commit` is the one that comes and goes, and
#: `status` says exactly when — see `STATUS`.
REQUIRED_COMPONENT_KEYS = ("name", "where", "status")

#: ⛔ Whether a component exists yet, as a **closed set**. ⭐ Ruling 54: the pin
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


def head_of(directory: Path) -> str | None:
    """Return the commit `directory` is on, or `None` if it is not a checkout."""
    if not directory.is_dir():
        return None
    result = git(directory, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else None


def holds(directory: Path, commit: str) -> bool:
    """Say whether this checkout holds that commit at all."""
    return git(directory, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def is_ancestor(directory: Path, commit: str, of: str) -> bool:
    """Is `commit` reachable from `of`? ⚠️ Equal counts, as `--is-ancestor` says."""
    return git(directory, "merge-base", "--is-ancestor", commit, of).returncode == 0


def verify(workspace_root: Path, repository_root: Path) -> list[str]:
    """Every way the checkouts disagree with the pin file. Empty means correct.

    ⛔ **Both directions, and the second is the one nobody thinks of.** A
    recorded commit **absent locally** means the pin points at nothing; a
    component's `HEAD` **moved unrecorded** means the pin is stale and a build
    that reproduced it would reproduce the wrong thing. ⚠️ Neither has a
    symptom — that is why this exists and why both are asserted rather than
    described.

    ⛔ **And a third question, which is not a direction of the first two**
    (`W402`): a sibling's **working tree**. A pin records a commit, so a
    checkout mid-merge, or holding a task's files staged and uncommitted, is at
    the commit recorded and still unreproducible — `checkout.uncommitted` names
    each such state, and the module beside this one argues why `self` is exempt.
    """
    workspace_root = Path(workspace_root)
    repository_root = Path(repository_root)
    findings: list[str] = []
    for component in read(repository_root):
        directory = component.directory(workspace_root, repository_root)
        head = head_of(directory)
        if not component.present:
            # ⛔ A third direction, and it is what makes `not-yet-created` a
            # register entry rather than a note. The day E12 creates the
            # component, this reds until somebody flips the status — so the
            # row cannot be created and forgotten.
            if head is not None:
                findings.append(
                    f"{component.name}: recorded as not created yet, and a "
                    f"checkout is there — record it and set status to 'present'"
                )
            continue
        if head is None:
            findings.append(f"{component.name}: no checkout found beside this repository")
            continue
        if component.where == "sibling":
            # ⛔ **The working tree, which a commit cannot carry** (`W402`).
            # Everything above reads `HEAD`, so a sibling in an abandoned merge
            # with a task's files staged and none committed reads green while
            # holding work that exists on no ref. ⭐ Reported in ADDITION to the
            # pin comparison, never instead of it: they are two questions, and a
            # checkout can be wrong in both at once.
            #
            # ⚠️ **`self` is exempt, and it is the same asymmetry ancestry is.**
            # The `self` row cannot be checked for equality because the file is
            # inside the commit; it is not checked for dirt because it is the
            # tree the reader is standing in and editing — an uncommitted pin
            # file is the normal working state (`record` writes one), so failing
            # on it would make a check that runs every round permanently red.
            # ⭐ A sibling is the checkout nobody is looking at, which is exactly
            # where the blindness was measured.
            findings.extend(f"{component.name}: {said}" for said in uncommitted(directory, git))
        if not holds(directory, component.commit):
            findings.append(
                f"{component.name}: the recorded commit {component.commit[:12]} "
                f"is not in that checkout"
            )
            continue
        if component.where == "self":
            # ⛔ Ancestry, not equality: a file cannot hold the hash of the
            # commit that holds it. The module docstring states why.
            if not is_ancestor(directory, component.commit, head):
                findings.append(
                    f"{component.name}: the recorded commit {component.commit[:12]} "
                    f"is not an ancestor of HEAD {head[:12]}"
                )
        elif head != component.commit:
            findings.append(
                f"{component.name}: HEAD is {head[:12]} and the pin file records "
                f"{component.commit[:12]} — advance the pin or check the component out"
            )
    return findings


def record(workspace_root: Path, repository_root: Path) -> dict:
    """Return the document that pins every component to what is checked out now.

    ⚠️ Reads the existing file for its component **list** and each row's
    `status`; only the commits change. ⛔ A component is not discovered by
    running this — a version that walked the workspace would pin whatever
    happened to sit beside the repository that day. ⭐ And a `not-yet-created`
    row keeps its status: flipping it is the decision E12 and E13 make, in the
    commit that creates the repository.
    """
    workspace_root = Path(workspace_root)
    repository_root = Path(repository_root)
    rows = []
    for component in read(repository_root):
        row = {"name": component.name, "where": component.where, "status": component.status}
        if component.present:
            head = head_of(component.directory(workspace_root, repository_root))
            row["commit"] = head or component.commit
        rows.append(row)
    return {"workspace_api": WORKSPACE_API, "components": rows}


def render(document: dict) -> str:
    """Render the pin file's exact bytes. ⛔ One serialisation, so a re-record is a no-op (R10)."""
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
