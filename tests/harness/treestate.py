"""Whether a run changed the working tree, as a **delta** rather than a verdict on cleanliness.

⭐ **`REL-02`: the product suite's OWN copy of `tools/treestate.py`**, so the suite's exit
condition holds in a checkout with no tooling in it. ⛔ The functions are that module's,
byte for byte save the file a failure points its reader at, and `tests/test_process_twins.py`
refuses a drift while both exist; `REL-10` leaves this copy as the only one.

**What it does.** Takes two `git status` snapshots and reports every path whose
status changed **between** them. Nothing else: it does not know what a writer
is, it does not read `src/`, and it has no list of files anybody is allowed to
create.

**How you use it.** `snapshot(root)` before the work and again after, then
`changes(before, after, exempt_prefixes(root, os.environ))`. `report(...)` is
the text a failure prints. `conftest.py` is what wires it to the suite.

**Depends on.** `dataclasses`, `os`, `pathlib` and `subprocess` — the standard
library, and `git` on the path. Nothing from `studyforge` and nothing from
the tooling: a check on what a test run left behind must not itself depend
on the tree being importable.

## ⛔ Why a delta and not "the tree is clean"

⚠️ The obvious check — *assert `git status` is empty after the suite* — is a
false-positive machine. Every contributor runs the suite with edits in flight,
so it would be RED for the ordinary case and GREEN only for somebody who has
just committed. ⛔ A check that is red by default is a check that gets an
environment variable to switch it off within a week.

⭐ A delta is red only for a path whose status **moved while the suite ran**,
which is the actual question. It is therefore also indifferent to what another
office merged on top: a merge changes the tree *before* the run, so both
snapshots see the same thing and the delta is empty. The one way a merge turns
this red is a merged branch that really does write during the run — which is
the signal, not noise.

## ⛔ What it cannot see, said here rather than discovered later

1. ⛔ **A path `.gitignore` covers is invisible**, because `--ignored` is not
   passed. That is deliberate and it is not free: `__pycache__/`,
   `.pytest_cache/` and `.scratch/` all move on every single run, so a snapshot
   that included them would never be equal to another one. ⭐ The cost is a
   blind spot exactly the size of the ignore file; the alternative is an
   instrument that is always red, which sees nothing at all.
2. ⛔ **A write outside the repository is invisible.** MEASURED at `abee048`
   with an audit hook over the emission census: eight public callables attempt
   `os.mkdir` under the probe's synthetic poison path, and every one of them
   fails only because the process is unprivileged. Nothing here would notice if
   one succeeded — this instrument answers *"did the run dirty the checkout"*
   and no larger question.
3. ⚠️ **`git` may not be installed.** Then there is no snapshot and the caller
   is told so **out loud**: a check over nothing must not return the pass
   reading (Ruling 191). `snapshot` returns `None` and never `{}`, because an
   empty mapping is a real answer — a clean tree — and the two must not be
   confusable.

## ⭐ The one exemption, and it is read from a declaration

`STUDYFORGE_VISUAL_CAPTURES` names a directory `tests/visual/conftest.py`
creates and fills with PNGs; the wrapper's own documentation says a path under
the checkout is what reaches the checkout. ⛔ That is a write the caller
**asked for**, so it is exempted by reading the same variable the harness reads
— never by naming a path here. Nothing else is exempt.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

#: The one git invocation. ⛔ `-z` because a path may contain a space or a
#: newline and the porcelain v1 text form quotes those; the NUL form does not,
#: so nothing here has to un-quote anything.
STATUS_ARGV = ("status", "--porcelain=v1", "--untracked-files=all", "-z")

#: How long git gets to answer before this is treated as "git could not tell
#: you" rather than as a verdict.
TIMEOUT_SECONDS = 60

#: The environment variable that legitimately points a run's output into the
#: checkout. ⚠️ Read, never hard-coded to a path — see the module docstring.
CAPTURE_VARIABLE = "STUDYFORGE_VISUAL_CAPTURES"

#: Status codes for a path git is not tracking at all.
UNTRACKED = "??"


@dataclass(frozen=True, order=True)
class Change:
    """One path whose git status moved while the run was in progress."""

    path: str
    before: str | None
    after: str | None

    def __str__(self) -> str:
        """Name the path and both states, in the words a reader needs."""
        return f"{self.path}\n      {_state(self.before)} -> {_state(self.after)}"


def _state(code: str | None) -> str:
    if code is None:
        return "absent from git status (clean, or not present)"
    if code == UNTRACKED:
        return "untracked"
    return f"status {code!r}"


def snapshot(root: Path) -> dict[str, str] | None:
    """Every path git reports in `root`, mapped to its two-letter status code.

    ⛔ Returns `None` — never `{}` — when git cannot answer. An empty mapping
    is the *clean tree* answer and a caller must be able to tell the two apart.
    """
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", *STATUS_ARGV],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except OSError, subprocess.SubprocessError:
        return None
    if result.returncode != 0:
        return None
    return _parse(result.stdout)


def _parse(payload: str) -> dict[str, str]:
    """Turn `git status --porcelain=v1 -z` output into `{path: code}`.

    ⚠️ A rename entry spends **two** NUL-separated fields — the destination
    then the origin — so the walk consumes rather than iterates. Reading it as
    one field per record would attribute the origin path to the next entry's
    code, which is a wrong answer that looks like a right one.

    ⛔ **The code is the first TWO columns and the path starts at the fourth,
    fixed-width** — never a split on the first space. A staged addition is
    `"A  alpha"`, so partitioning on a space yields the path `" alpha"` with a
    leading blank: the same file under two different keys, which reads as a
    change in every delta. MEASURED here by `test_a_file_edited_during_the_run…`
    before this line said so.
    """
    fields = [field for field in payload.split("\0") if field]
    found: dict[str, str] = {}
    index = 0
    while index < len(fields):
        entry = fields[index]
        index += 1
        code, path = entry[:2], entry[3:]
        if not path:
            continue
        found[path] = code
        if "R" in code or "C" in code:
            index += 1  # the origin path, which is not a change of its own
    return found


def exempt_prefixes(root: Path, environ: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Repository-relative prefixes a run was **asked** to write into.

    ⭐ Today that is the visual capture directory and nothing else, and it is
    here only when the caller pointed it inside the checkout.
    """
    named = (environ if environ is not None else os.environ).get(CAPTURE_VARIABLE, "").strip()
    if not named:
        return ()
    try:
        relative = Path(named).resolve().relative_to(Path(root).resolve())
    except ValueError:
        return ()  # outside the checkout: nothing here can see it anyway
    return (relative.as_posix().rstrip("/") + "/",)


def changes(
    before: dict[str, str] | None,
    after: dict[str, str] | None,
    exempt: tuple[str, ...] = (),
) -> list[Change] | None:
    """Every path whose status differs between the two snapshots.

    ⛔ `None` when either snapshot is missing, propagating "git could not tell
    you" rather than converting it into "nothing changed".
    """
    if before is None or after is None:
        return None
    moved = [
        Change(path, before.get(path), after.get(path))
        for path in sorted(set(before) | set(after))
        if before.get(path) != after.get(path) and not _is_exempt(path, exempt)
    ]
    return moved


def _is_exempt(path: str, exempt: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in exempt)


def report(moved: list[Change]) -> str:
    """Render what a dirtied tree prints, in the form the reader has to act on."""
    lines = [
        f"the working tree changed while the suite ran: {len(moved)} path(s)",
        "⛔ a test wrote into the checkout. Two instances of this have already been "
        "measured, and one of them turned an unrelated module's test RED.",
    ]
    lines += [f"  - {change}" for change in sorted(moved)]
    lines.append(
        "⚠️ blind to paths .gitignore covers, and to writes outside the repository — "
        "see tests/harness/treestate.py"
    )
    return "\n".join(lines)
