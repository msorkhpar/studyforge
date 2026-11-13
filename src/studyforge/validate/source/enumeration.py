r"""What the corpus root holds as material, asked of the repository and the plan.

**What it does.** Enumerates the corpus root: every file that is material rather
than output, and every nested repository store. It gives no verdict;
`classification` judges what it returns.

**How you use it.** `source_files(root)` returns a `Scan`. `repository_ignores` is
the one ignore reader, `restorable` says whether git could give back what a
removal would take, and `REPOSITORY_STORE` and `SKIP_DIRS` name what a walk
never enters.

**Depends on.** `corpus.placement`, `cli.plan` for what a build writes (deferred,
`_generated_output` says why), and `git` on the path. ⛔ **No other module of this
package**: `classification` reads this one, never the other way round.

## ⛔ What counts as material is the corpus's declaration, not this file's guess

⭐ **The repository already says which of its files are generated, and
`source_files` asks it.** Spec §11.2 clause 11 named `git status` from the
start; the code simply never implemented the definition it had been given, and
A framework-kept list of directory names to skip (`node_modules`,
`__pycache__`) is the framework knowing about ecosystems, which is R1 with the
sign flipped.

⚠️ **A real corpus's walk can be mostly its own declared output**, and
reporting all of it as unclassified material files the few genuinely withheld
files among a hundred that were never material — an audit nobody reads, the
exact failure `content.exclude`'s mandatory `why` exists to prevent.

⚠️ **And the number has no fixed point.** A generated directory grows by the
hour, so a framework carrying its own exclusion list is wrong again tomorrow. The declaration
moves with the corpus because it belongs to the corpus.

## ⛔ A build's own output is recognised from the plan, not ignored and not declared

⭐ **A build's pages and media are committed** (§5), so git does not
declare them output. `studyforge plan` already enumerates them from this
corpus's declarations, so the scan asks it: a planned file is recognised by
its exact path, and everything under a planned directory is recognised with it.
⚠️ No glob. The manifest refuses a leading-wildcard
`not_material` glob, because its correctness depends on which files happen not
to exist. A placed path doesn't. ⛔ A planned path the manifest includes as
material is `contested`, never resolved by precedence. A plan that refused
recognises nothing, and the report says so.

## ⛔ An ignored directory is pruned as the walk reaches it, and the answer does not move

⚠️ **Walking everything and only then asking git is the slow half**: a
virtualenv or a worktree under an ignored folder is gigabytes thrown away. ⭐
So git is asked once, before the walk, which directories it holds wholly
ignored and untracked (`_ignored_directories`), and the walk never enters
them. ⛔ **A scan returns exactly what the full walk returns**: each file under
such a directory is one `repository_ignores` drops, a directory holding a
planned path is still walked, and when git cannot judge the files the scan
walks everything again.

⛔ **A root that is not a git working tree gets the old walk and an
`Unchecked`** (`ignore-declaration`), never a guess. Same rule as the absent
source tree in `completeness`, for the same reason: a half-applied ignore rule
is a half-present input, and the dangerous half is the one that looks clean.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.placement import ARCHIVE_DIRNAME

#: The name of a repository's store, a directory or a submodule's gitfile.
REPOSITORY_STORE = ".git"

#: What a source scan never enters, **at the corpus root only**.
#:
#: ⛔ **These two are the framework's own and nobody else's.** `.studyforge` is
#: this tool's, and `.git` holds the declaration this module now reads rather
#: than guesses at. ⚠️ **Beneath the root neither is the framework's**: a
#: nested `.studyforge` is material, and a nested `.git` is refused by name
#: (`RULE_NESTED_REPOSITORY`). ⚠️ **The archive root is not here**: it
#: is skipped at the corpus root only, and `membership` refuses each file
#: beneath it that is not an archive member. A source's own nested `archive/`
#: is material.
#: No ecosystem's directory (`node_modules`, `__pycache__`) is here: that would
#: be the framework knowing about ecosystems it was told nothing about (R1), and
#: wrong for any corpus that uses another.
SKIP_DIRS = (".git", ".studyforge")

#: How long git is given to answer. ⚠️ A validator that hangs is worse than one
#: that says it could not check.
IGNORE_TIMEOUT = 30


@dataclass(frozen=True, slots=True)
class Scan:
    """What the corpus root holds as material, and whether it was asked.

    ⛔ **One value, because the two halves may never be read apart.** A caller
    that took the file list without `consulted` would report a hundred
    generated files as unclassified and print a clean-looking run; a caller
    that took `consulted` without the list would have nothing to classify. The
    fallback and the announcement of the fallback are the same fact.
    """

    files: tuple[Path, ...]
    consulted: bool
    #: ⭐ The files a build of this corpus writes, recognised by the plan and
    #: therefore not in `files`. Carried rather than dropped, so an instrument
    #: can print the population it judged.
    generated: tuple[Path, ...] = ()
    #: ⛔ False when the plan refused: nothing was recognised, which is not
    #: the same as nothing having been generated.
    planned: bool = True
    #: ⛔ Each nested repository store the repository does not declare as
    #: output, refused by name. Its contents are never in `files`.
    stores: tuple[Path, ...] = ()


def source_files(root: Path) -> Scan:
    """Every file in the corpus root that is material rather than output.

    ⭐ **The corpus already declares what is output, and this asks it.** Spec
    §11.2 clause 11 names `git status`; what this reads is the same
    declaration, one call, in the file every repository has. That is why it is
    R1-clean: no ecosystem is named here, and the answer arrives as data from
    the source rather than as a list of names the framework carries.

    ⚠️ **Where the root is not a git working tree the walk stands and the
    caller says so** — see `Scan`. Refusing a non-repository corpus is wrong
    (R2: an archive is a shippable artifact on its own), and quietly scanning
    everything is worse than either, because it looks like a clean run.
    """
    planned = _planned(root)
    pruned = _ignored_directories(root, planned)
    scan = _scan(root, planned, pruned)
    if pruned and not scan.consulted:
        # ⛔ The fallback lists everything, so nothing may have been pruned.
        return _scan(root, planned, frozenset())
    return scan


def _scan(root: Path, planned: _Planned | None, pruned: frozenset[Path]) -> Scan:
    """`source_files`' answer for one walk that never enters `pruned`."""
    walked, stores = _walk(root, pruned)
    recognised = _generated_output(planned, walked)
    generated = tuple(path for path in walked if recognised and path in recognised)
    candidates = [path for path in walked if not recognised or path not in recognised]
    declared = repository_ignores(root, candidates + stores)
    if declared is None:
        return Scan(
            tuple(candidates),
            consulted=False,
            generated=generated,
            planned=planned is not None,
            stores=tuple(stores),
        )
    files = tuple(path for path in candidates if path not in declared)
    refused = tuple(store for store in stores if store not in declared)
    return Scan(
        files, consulted=True, generated=generated, planned=planned is not None, stores=refused
    )


@dataclass(frozen=True, slots=True)
class _Planned:
    """What a build of this corpus writes: exact files, and directories it fills."""

    files: frozenset[Path]
    directories: tuple[Path, ...]

    def touches(self, directory: Path) -> bool:
        """Whether anything planned lies under `directory`, or `directory` under a planned one."""
        return any(path.is_relative_to(directory) for path in self.files) or any(
            planned.is_relative_to(directory) or directory.is_relative_to(planned)
            for planned in self.directories
        )


def _planned(root: Path) -> _Planned | None:
    """The plan's own enumeration of what a build writes, or `None` when the plan refused.

    ⛔ **The plan's answer, never a list here**. A plan line
    ending in `/` is a directory whose contents a build or `narrate` fill, and
    every other line is a file — the plan's printed distinction, which
    `generate.footprint` reads the same way. ⚠️ Unlike a footprint, a unit's
    audio directory IS a prefix here: narrate's clips are generated media
    whoever wrote them.

    ⚠️ **The import is deferred, for `generate.footprint`'s reason:** `cli`
    imports the dispatcher, which imports this package.
    """
    from studyforge.cli.plan import plan_for

    plan = plan_for(root)
    if plan.refusals:
        return None
    return _Planned(
        files=frozenset(root / path for path in plan.paths if not path.endswith("/")),
        directories=tuple(root / path.rstrip("/") for path in plan.paths if path.endswith("/")),
    )


def _generated_output(planned: _Planned | None, candidates: list[Path]) -> frozenset[Path] | None:
    """Which of `candidates` a build of this corpus writes, by the plan's own enumeration.

    ⛔ **`None` when the plan refused.** An incomplete enumeration recognises
    nothing, and the caller says so.
    """
    if planned is None:
        return None
    # ⚠️ A set of directories asked once per ancestor, never every directory per file:
    # a course plans hundreds of directories and holds thousands of files.
    directories = frozenset(planned.directories)
    return frozenset(
        path
        for path in candidates
        if path in planned.files
        or path in directories
        or not directories.isdisjoint(path.parents)
    )


def _ignored_directories(root: Path, planned: _Planned | None) -> frozenset[Path]:
    """The directories under `root` that git holds wholly ignored and untracked.

    ⭐ **One question to git, asked before the walk**: `ls-files --others
    --ignored --directory` names a directory, rather than its files, when
    everything in it is ignored and nothing in it is tracked, and it does not
    descend into an ignored directory to say so. That is what keeps a
    virtualenv or a worktree under an ignored folder out of the walk.

    ⛔ **Only a pruning hint**: `repository_ignores` still judges every file
    the walk finds, and an empty set (no git, no answer) prunes nothing.
    ⚠️ A directory that holds or lies under a planned path is not pruned: the
    scan reports those files as `generated` whether or not git ignores them.
    """
    git = shutil.which("git")
    if git is None:
        return frozenset()
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--directory"],
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            timeout=IGNORE_TIMEOUT,
        )
    except OSError, subprocess.SubprocessError:
        return frozenset()
    if result.returncode != 0:
        return frozenset()
    directories = {
        root / name.rstrip("/") for name in result.stdout.split("\0") if name.endswith("/")
    }
    if planned is None:
        return frozenset(directories)
    return frozenset(directory for directory in directories if not planned.touches(directory))


def _walk(root: Path, pruned: frozenset[Path] = frozenset()) -> tuple[list[Path], list[Path]]:
    """Every file under `root` that is not the framework's own writing, and every nested store.

    ⛔ **`SKIP_DIRS` is asked of the first part only**: a nested
    `.studyforge` is walked like any directory. A nested `.git`, directory or
    gitfile, is returned as a store and never entered. ⭐ A directory in
    `pruned` is never entered either.

    ⚠️ **Symbolic links are not followed**: a link to a file is read as that
    file, and a link to a directory is neither a file nor entered.
    """
    found: list[Path] = []
    stores: set[Path] = set()
    if root in pruned:
        return found, []
    for directory, dirnames, filenames in os.walk(root):
        here = Path(directory)
        at_root = here == root
        kept = []
        for name in dirnames:
            path = here / name
            if at_root and (name in SKIP_DIRS or name == ARCHIVE_DIRNAME):
                # ⛔ Not silent: `membership` accounts for every archive file.
                continue
            if name == REPOSITORY_STORE:
                stores.add(path)
                continue
            if path in pruned:
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in filenames:
            path = here / name
            if at_root and (name in SKIP_DIRS or name == "corpus.json"):
                continue
            if name == REPOSITORY_STORE:
                stores.add(path)
                continue
            if path.is_file():
                found.append(path)
    return sorted(found), sorted(stores)


def repository_ignores(root: Path, candidates: list[Path]) -> frozenset[Path] | None:
    """Which of `candidates` the repository declares as generated output.

    ⭐ **Public because it is the ONE ignore reader, and a second
    caller imports it rather than keeping a list**: the scaffolded
    `test_emit` asks it which directories a working copy leaves behind.

    ⛔ **Git's own answer, never a reimplementation of it.** Ignore rules have
    precedence, negation, per-directory files, an index that makes a tracked
    file un-ignorable and a user's global configuration. A framework that
    reproduced four of those five would be wrong on the fifth, silently, in
    somebody else's repository.

    ⛔ **`None` means "not answered", and it is not the same as "nothing is
    ignored".** Fail-open is what this refuses: the caller turns
    `None` into an `Unchecked`, loudly and counted, exactly as an absent source
    tree is reported. An empty frozenset means git answered "none of them".

    ⚠️ One subprocess for the whole tree, never one per file — `--stdin` takes
    the batch, and `-z` is what makes a filename with a newline in it a
    pathname rather than two.
    """
    git = shutil.which("git")
    if git is None:
        return None
    try:
        names = [path.relative_to(root).as_posix() for path in candidates]
    except ValueError:
        # ⛔ R7: `relative_to`'s own message quotes both paths, and `root` is the
        # one input guaranteed to carry a home directory (the census).
        raise ValueError("a candidate is not beneath the root it was asked about") from None
    payload = "\0".join(names)
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "check-ignore", "--stdin", "-z"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            timeout=IGNORE_TIMEOUT,
        )
    except OSError, subprocess.SubprocessError:
        return None
    # 0: some path is ignored. 1: none is. 128: not a repository, or worse —
    # and "or worse" is exactly why an unexpected code is not read as "none".
    if result.returncode not in (0, 1):
        return None
    return frozenset(root / name for name in result.stdout.split("\0") if name)


def restorable(root: Path, paths: list[str]) -> bool | None:
    """Whether git could restore every file under `paths` as it is now, with nothing staged.

    ⭐ **Asked before anything is removed**, so a removal is one `git restore`
    away from undone. ⛔ `True` only when the index holds no staged change and
    no file under `paths` is untracked, ignored, modified or staged: each of
    those is a byte git could not give back. ⛔ **`None` means "not answered"**
    — no git, or `root` not in a work tree — and a caller treats it as `False`.
    """
    git = shutil.which("git")
    if git is None:
        return None
    # ⛔ `:(literal)`: a path is matched as written, never as a glob.
    named = [f":(literal){path}" for path in paths]
    try:
        staged = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "diff", "--cached", "--quiet"],
            capture_output=True,
            cwd=root,
            check=False,
            timeout=IGNORE_TIMEOUT,
        )
        changed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [
                git,
                "status",
                "--porcelain",
                "-z",
                "--untracked-files=all",
                "--ignored",
                "--",
                *named,
            ],
            capture_output=True,
            cwd=root,
            check=False,
            timeout=IGNORE_TIMEOUT,
        )
    except OSError, subprocess.SubprocessError:
        return None
    # `diff --quiet`: 0 nothing staged, 1 something is. Anything else is unanswered.
    if staged.returncode not in (0, 1) or changed.returncode != 0:
        return None
    return staged.returncode == 0 and not changed.stdout
