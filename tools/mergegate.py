"""`W302`: a merge to a release branch READS BOTH ENVIRONMENTS on the MERGED TREE, and branches.

**What it does.** Stages a merge without committing it, runs every gate in `GATES` against
the tree that merge produced, and commits only when every one of them exits `0`. On a red
reading it runs `git merge --abort` and then VERIFIES the restore BY READING THE TREE —
`HEAD` is back where it started and the tracked tree is clean — because a restore command's
own exit code is not a restore (Rulings 205, 287). Exit `0` merged, `1` a gate refused and
nothing was committed, `2` nothing was read.

⭐ **It STOPS AT THE FIRST RED.** The merge is refused the moment one gate refuses, so a
later gate cannot change the outcome — and a refusal that costs the office a whole second
environment is a refusal somebody eventually works around. ⛔ The gates that were therefore
NOT taken are NAMED in the reading, never silently dropped: *nothing was printed* and
*there was nothing to say* must not be the same line (`FND-07`, Ruling 78's shape).

**How you use it.** It IS the merge, so there is no way to take the merge without it:

    python3 -m tools.mergegate <branch> --body <file>
    python3 -m tools.mergegate <branch> --body <file> --stage-only
    python3 -m tools.mergegate <branch> --body <file> --full "<why: a milestone close>"

`stage_and_read(root, branch, runner)` returns the `Outcome` the command prints, and
`render(outcome)` gives the printed lines. The clause lives in
`docs/conventions/board.md`, beside Ruling 231(b).

**Depends on.** `argparse`, `dataclasses`, `pathlib`, `subprocess` and `sys` — the standard
library — `git` on the path, `tools.authorship` for the one question this file does not
answer, and `tools.gates` for WHICH commands are the gates and whether each suite is taken
serial or parallel (`W364`), `tools.selection` for WHICH TESTS a suite gate takes and
`tools.mergereading` for what a reading is and prints (`W366`). The gates it RUNS are
subprocesses named there; this module imports neither `studyforge` nor `tools.quality`, so a
tree too broken to import is still one whose merge is refused rather than one that crashes
the gate.

## ⛔ WHY IT IS A COMMAND AND NOT A FLOOR CHECK — the wall `W296` met

⚠️ **The naive remedy is *add it to `tools.quality.CHECKS`*, and an existing ruling refuses
it.** ⭐ The argument is `board/corroborate.py`'s and is CITED rather than re-derived:

- ⛔ **Ruling 80** — a floor check's verdict may not depend on untracked state, and a branch
  position is the purest untracked state there is.
- ⛔ **R10** — the floor is byte-for-byte reproducible over arbitrary roots, where there is
  no release branch and no docker daemon at all.
- ⛔ **Ruling 191** — a floor check that shelled into git and found no branch would return
  THE PASS READING FROM AN EMPTY POPULATION. ⭐ Here that is impossible by construction: a
  run that reads no gate exits `UNREAD` and never `MERGED`.

⭐ **So it is a COMMAND, like `subject.py`, `gated.py` and `trial.py`, and it is in neither
`CHECKS` nor `NOTICES`.** ⛔ The mirror asserts that.

## ⛔ WHY THE PAIR IS THE UNIT, AND NEITHER ENVIRONMENT MAY BE SWAPPED FOR THE OTHER

⚠️ **MEASURED at `d35262f`, role `wt/dev1`, both routine environments, one ref:** collection
AGREES and the delta is ENTIRELY SKIPS — the host does not reach the `ruff` enforcement or
the in-image assertions, and the pinned image does not reach the sibling/workspace ones,
because it mounts only the checkout (Ruling 248(a)). ⛔ **A gate that swapped one for the
other would trade a blind spot rather than close it**, which is why `GATES` names both and
every entry is required.

⚠️ **What this does NOT gate is which tests an environment could REACH.** ⛔ A skip census
is a property of the HOST, not of the branch, so Ruling 328 makes it a DISCLOSURE: the
suite already prints it (`report.unreachable_population`), and nothing here reads it.

## ⛔ WHAT IT MUST NOT BECOME (the row)

- ⛔ **A SECOND COPY OF THE LINT RULES.** `tests/test_repository.py` already fails the build
  wherever `ruff` exists (Ruling 78). ⭐ This RUNS that and BRANCHES ON ITS EXIT; it never
  restates a rule, and it names no linter.
- ⛔ **A REPORT OVER LANDED TIPS.** It reads the tree being merged and NEVER history: a
  backlog over frozen tips is one no office may clear (`subject.py`'s own clause).
- ⛔ **A GATE THAT COMMITS ANYTHING ON A RED READING.** `--no-commit` is what makes the
  refusal free: there is no commit to undo, and `--abort` restores exactly.

## ⛔ `W364` CLAUSE 6 — IT HOLDS THE SHARED CONTAINER LOCK ITSELF, AND ONLY FOR THE IMAGE

⚠️ **Measured by the register:** a merge run wrapped WHOLE in the shared container lock held
it through the HOST suite too — minutes of lock time that used no container, while every
office's container reading queued behind it. ⭐ So when `STUDYFORGE_CONTAINER_LOCK` names a
lock file, this command takes an exclusive `fcntl.flock` on it around the consecutive
pinned-image gates ONLY and releases it before any host gate. ⛔ Unset, it locks nothing and
behaves exactly as before. The path is read from the environment and written nowhere; the
lock itself is `tools.gates.ContainerLock`, beside the form each gate is taken in.

## ⛔ `W366` — THE SUITE TAKES WHAT THE CHANGE CAN REACH, AND A FULL RUN AUDITS THAT

⭐ After staging, `tools.selection.decide` reads what the branch changed and scopes every SUITE
gate: the test files those paths reach, or the full suite for shared machinery, an unknown
kind of path, every `AUDIT_EVERY`-th merge, or `--full`. ⛔ The reading SAYS which — a
targeted GREEN is never printed as a full one — and a full run that audits names every
failure the selection would have missed. ⭐ To make that readable the real runner TEES the
gate's stdout rather than letting it pass untouched. The floor is never scoped.

## ⛔ WHO WROTE IT IS READ TOO, AND IT IS A SEPARATE MODULE (`W308`)

⭐ **`tools/authorship.py` answers *who wrote the commits this merge introduces*; this file
answers *what the tree that merge produces reads*** — the seam is that question, and the
argument lives THERE rather than in two copies (Ruling 261: a SPLIT, never a trim).
⚠️ It runs BEFORE the merge is staged, so its refusal leaves no tree to restore, which is
why `Outcome.verdict` answers it first and never consults `restored`.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path

from tools.authorship import Authorship, read_authorship

# ⭐ `W364`: the gates, and the serial or parallel form each suite takes, are declared in
#    `tools.gates` (a SPLIT, Ruling 261) and re-exported here, where every caller reads them.
from tools.gates import GATES, HOST, IMAGE, LOCK_VARIABLE, ContainerLock, Gate, declared, scoped

# ⭐ `W366`: what a run READ and how it prints live in `tools.mergereading` (a SPLIT, Ruling 261).
from tools.mergereading import MERGED, REFUSED, UNREAD, Outcome, Reading, render
from tools.selection import decide, describe, failed_ids

__all__ = [
    "GATES",
    "HOST",
    "IMAGE",
    "LOCK_VARIABLE",
    "MERGED",
    "REFUSED",
    "UNREAD",
    "ContainerLock",
    "Gate",
    "Outcome",
    "Reading",
    "declared",
    "main",
    "render",
    "stage_and_read",
]

#: What a gate's exit code is read through. ⛔ Injected so the mirror can assert both
#: directions without a docker daemon; the default is the real thing.
#: ⭐ `W366`: a runner MAY also return the test ids its output named as failed — the real
#: one does, so a full run can AUDIT the selection; a bare exit code names none.
Runner = Callable[[Gate, Path], int | tuple[int, tuple[str, ...]]]


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    """Run git in `root` and return its exit code with its stripped stdout."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), *arguments],  # noqa: S607 - git from the path, by design
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def run_gate(gate: Gate, root: Path, failed: list[str] | None = None) -> int:
    """Run one gate in `root` and return its exit code, letting its output through.

    ⭐ `W366`: given a `failed` list — a FULL run auditing the selection — stdout is TEED: each
    line is printed as it arrives and every test id pytest's summary names as failed is
    appended. Without one the gate runs exactly as it always has; stderr is never touched.
    """
    try:
        if failed is None:
            return subprocess.run(  # noqa: S603 - fixed argv from GATES, no shell
                list(gate.argv), cwd=root, check=False
            ).returncode
        with subprocess.Popen(  # noqa: S603 - fixed argv from GATES, no shell
            list(gate.argv), cwd=root, stdout=subprocess.PIPE, text=True, errors="replace"
        ) as process:
            for line in process.stdout or ():
                sys.stdout.write(line)
                sys.stdout.flush()
                failed.extend(failed_ids([line]))
            return process.wait()
    except OSError:
        return UNREAD


def _take(gate: Gate, root: Path) -> int | tuple[int, tuple[str, ...]]:
    """Run `gate` the default way: `run_gate`, teed only when it AUDITS a selection (`W366`)."""
    if gate.audit is None:
        return run_gate(gate, root)
    failed: list[str] = []
    return run_gate(gate, root, failed), tuple(failed)


def tracked_changes(root: Path) -> str | None:
    """Return git's tracked-porcelain for `root`, or None when git cannot answer."""
    code, out = _git(root, "status", "--porcelain", "--untracked-files=no")
    return None if code != 0 else out


def stage_and_read(
    root: Path,
    branch: str,
    runner: Runner | None = None,
    gates: Sequence[Gate] | None = None,
    full: str = "",
) -> Outcome:
    """Stage the merge of `branch`, read every gate on the MERGED tree, and abort on red.

    ⛔ Nothing is committed here. The merge is staged with `--no-commit`, so a red reading
    ends in `git merge --abort`, which restores exactly — and the restore is then VERIFIED
    by reading `HEAD` and the tracked tree, never by the abort's own exit code.
    """
    # ⛔ Resolved HERE and not as a default argument: a default binds the function object at
    #    definition, so a mirror could never substitute a runner and every test would need a
    #    docker daemon to reach this code at all.
    take = _take if runner is None else runner
    # ⭐ `W364`: unless told otherwise, the gates THIS host can take — the host suite is
    #    parallel only where its own `python3` imports `xdist`, and the reading says so.
    gates = declared() if gates is None else gates
    if not gates:
        return Outcome(unread="no gate is declared, so nothing was read")
    code, tip = _git(root, "rev-parse", "HEAD")
    if code != 0 or not tip:
        return Outcome(unread="git cannot read a HEAD in this tree")
    dirty = tracked_changes(root)
    if dirty is None:
        return Outcome(unread="git cannot read this tree's status", tip_before=tip)
    if dirty:
        return Outcome(
            unread="the tracked tree is not clean, so a merge would carry uncommitted work",
            tip_before=tip,
        )
    # ⛔ `git merge` and `git commit` BOTH need a committer, and the PINNED IMAGE CONFIGURES
    #    NONE — measured: `git config --get user.name` exits 1 in there. ⚠️ Without this the
    #    merge simply fails and the office is told "did not stage cleanly", which names the
    #    wrong thing entirely. ⭐ Asked of GIT ITSELF rather than of one config key, so an
    #    identity from the environment, a system file or a repository config all answer.
    identified, _ = _git(root, "var", "GIT_COMMITTER_IDENT")
    if identified != 0:
        return Outcome(
            unread=(
                "git has no committer identity here, so it can neither merge nor commit — "
                "pass one PER INVOCATION and set none: `git -c user.name=… -c user.email=…`"
            ),
            tip_before=tip,
        )
    # ⛔ `W308`, and it is read BEFORE the merge is staged: a carrier whose commits are not
    #    the office's own is refused while there is still nothing to abort. ⭐ The population
    #    is `HEAD..branch` — what this merge INTRODUCES — so no landed commit is ever judged.
    author = read_authorship(root, branch)
    if author.unread:
        return Outcome(unread=author.unread, tip_before=tip)
    if author.crossed:
        return Outcome(authorship=author, tip_before=tip)
    merged, _ = _git(root, "merge", "--no-ff", "--no-commit", branch)
    if merged != 0:
        _git(root, "merge", "--abort")
        return Outcome(unread=f"the merge of {branch} did not stage cleanly", tip_before=tip)

    # ⭐ `W366`: read on the MERGED tree, so a test the target branch added since this one
    #    was cut is in the import map. `full` names why the register asked for the whole suite.
    suites = any(gate.name == "suite" for gate in gates)
    scope = decide(root, branch, requested=full) if suites else None
    gates = gates if scope is None else scoped(tuple(gates), scope)
    said = () if scope is None else tuple(describe(scope))
    readings: list[Reading] = []
    # ⭐ `W364` clause 6: held across consecutive IMAGE gates, released before a HOST gate
    #    and on every way out of the loop — a red reading's early return included.
    lock = ContainerLock(os.environ.get(LOCK_VARIABLE, ""))
    try:
        outcome = _read_gates(root, gates, take, lock, readings, tip, author)
    finally:
        lock.hold(False)
    return replace(outcome, scope=said)


def _read_gates(
    root: Path,
    gates: Sequence[Gate],
    take: Runner,
    lock: ContainerLock,
    readings: list[Reading],
    tip: str,
    author: Authorship,
) -> Outcome:
    """Take each gate in order, under the lock when it is an image gate; stop at the first red."""
    for index, gate in enumerate(gates):
        lock.hold(gate.environment == IMAGE)
        taken = take(gate, root)
        code, failed = taken if isinstance(taken, tuple) else (taken, ())
        readings.append(Reading(gate, code, failed))
        if not readings[-1].green:
            # ⛔ STOP AT THE FIRST RED. The merge is refused already, so nothing a later
            #    gate says can change the outcome — and a refusal that costs the office a
            #    whole second environment is a refusal somebody works around. ⭐ The gates
            #    not taken are NAMED below, never silently dropped.
            outcome = Outcome(
                readings=tuple(readings),
                # ⛔ WITH its environment: two gates share the name `suite`, so a bare name
                #    leaves the reader unable to say WHICH one went unread (Ruling 326).
                not_taken=tuple(
                    f"{later.name} [{later.environment}]" for later in gates[index + 1 :]
                ),
                tip_before=tip,
                authorship=author,
            )
            _git(root, "merge", "--abort")
            return _verify_restore(root, outcome)
    return Outcome(readings=tuple(readings), tip_before=tip, authorship=author)


def _verify_restore(root: Path, outcome: Outcome) -> Outcome:
    """Read the tree back and report whether the abort put it where it started."""
    code, after = _git(root, "rev-parse", "HEAD")
    clean = tracked_changes(root)
    restored = code == 0 and after == outcome.tip_before and clean == ""
    return replace(outcome, tip_after=after, restored=restored)


def commit(root: Path, body: Path) -> int:
    """Commit the staged merge with `body` as its message, and return git's exit code."""
    code, _ = _git(root, "commit", "-F", str(body))
    return code


def main(argv: list[str] | None = None) -> int:
    """Stage, read every gate, then commit or abort; print the reading and return the exit."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.mergegate",
        description="Gate a merge on BOTH environments, read on the merged tree (W302).",
    )
    parser.add_argument("branch", help="the branch to merge")
    parser.add_argument("--body", type=Path, help="the merge message's body file")
    parser.add_argument("--root", type=Path, default=Path(), help="the checkout to merge in")
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="leave a green merge STAGED rather than committing it",
    )
    parser.add_argument(
        "--full",
        metavar="REASON",
        default="",
        help="take the FULL suite and audit the selection, saying why (a milestone close)",
    )
    arguments = parser.parse_args(argv)
    if arguments.body is None and not arguments.stage_only:
        parser.error("--body is required unless --stage-only is given")

    outcome = stage_and_read(arguments.root, arguments.branch, full=arguments.full)
    print("\n".join(render(outcome)))
    if outcome.verdict != MERGED or arguments.stage_only:
        return outcome.verdict
    if commit(arguments.root, arguments.body) != 0:
        print("⛔ UNREAD: every gate was green but the commit failed; the merge is STAGED")
        return UNREAD
    _, tip = _git(arguments.root, "rev-parse", "HEAD")
    print(f"⭐ MERGED: {tip[:12]}")
    return MERGED


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
