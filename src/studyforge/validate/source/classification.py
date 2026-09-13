r"""What the corpus says each of its files is — material, output, or nothing.

**What it does.** Enumerates the corpus root and refuses a file the manifest
classifies as neither included nor excluded, one it classifies as both, and
one it INCLUDES that no unit's origin names (`W266`).

**How you use it.** `check_unclassified(walk)`, yielding `Finding`s and
`Unchecked`s like every other check. `source_files(root)` is the enumeration
on its own, for a caller that wants the list rather than the verdict.

**Depends on.** `corpus.manifest` for the classification, `corpus.placement`, `validate.corpus`,
`validate.report`, `cli.plan` for what a build writes (deferred, `_generated_output` says why),
and `git` on the path. ⛔ **Nothing in this package's other
half** — the two checks share no name.

## ⛔ What counts as material is the corpus's declaration, not this file's guess

⭐ **The repository already says which of its files are generated, and
`source_files` asks it.** Spec §11.2 clause 11 named `git status` from the
start; the code simply never implemented the definition it had been given, and
`SKIP_DIRS` was the shape of the gap — five names, two of which
(`node_modules`, `__pycache__`) were the framework knowing about two
ecosystems, which is R1 with the sign flipped.

⚠️ **Measured against a real corpus, 2026-09-10:** of 159 files the walk
enumerated, **100 were the repository's own declared output** and every one was
reported as unclassified material. ⛔ **The three that were genuinely material
withheld from the reader were filed among a hundred that were never material at
all**, which is an audit nobody reads — the exact failure `content.exclude`'s
mandatory `why` exists to prevent, reached from the other side.

⚠️ **And the number has no fixed point.** The same generated directory held 79
files, then 91, then 96 within one day, so a framework carrying its own
exclusion list is a framework that is wrong again tomorrow. The declaration
moves with the corpus because it belongs to the corpus.

## ⛔ A build's own output is recognised from the plan, not ignored and not declared

⭐ **A build's pages and media are committed** (§5, `W242`), so git no longer
declares them output. `studyforge plan` already enumerates them from this
corpus's declarations, so the scan asks it: a planned file is recognised by
its exact path, and everything under a planned directory is recognised with it
(`INT-06/7`). ⚠️ No glob. The manifest refuses a leading-wildcard
`not_material` glob, because its correctness depends on which files happen not
to exist. A placed path doesn't. ⛔ A planned path the manifest includes as
material is `contested`, never resolved by precedence. A plan that refused
recognises nothing, and the report says so.

⛔ **A root that is not a git working tree gets the old walk and an
`Unchecked`** (`ignore-declaration`), never a guess. Same rule as the absent
source tree in `completeness`, for the same reason: a half-applied ignore rule
is a half-present input, and the dangerous half is the one that looks clean.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.manifest import Classification
from studyforge.corpus.placement import ARCHIVE_DIRNAME
from studyforge.validate.corpus import Walk
from studyforge.validate.report import Finding, Unchecked

RULE_UNCLASSIFIED = "unclassified"

#: ⛔ A file matched by **both** `include` and `content.not_material`, under
#: its own rule id rather than `unclassified`'s. ⭐ **Never a precedence**: the
#: manifest classified this file twice and disagreed with itself, which is a
#: different fact from never having classified it, and refusing it is what
#: stops the third state becoming somewhere to sweep material into.
RULE_CONTESTED = "contested"

#: ⛔ Its own rule id rather than `unclassified`'s. The classification check did
#: run; what could not be read is the repository's declaration of what is
#: output — a different fact, and one a script filters on separately.
RULE_IGNORE_DECLARATION = "ignore-declaration"

#: ⛔ A repository's store nested inside the corpus — a vendored repository or
#: a submodule checkout — refused by name, never skipped and never scanned
#: (`W259`). Its own rule id, because the fix is not a `content` pattern.
RULE_NESTED_REPOSITORY = "nested-repository"

#: ⛔ `W266`: a file the manifest INCLUDES that no UNIT's `origin` names, so no unit reads it —
#: an aggregate un-excluded, or a stray. ⚠️ A container's `origin` PLACES its page and reads
#: nothing. Judged over this scan only, while a unit origin is on disk (`origin-missing`).
RULE_INCLUDED_UNREAD = "included-unread"

#: The name of a repository's store, a directory or a submodule's gitfile.
REPOSITORY_STORE = ".git"

#: What a source scan never enters, **at the corpus root only** (`W259`).
#:
#: ⛔ **These two are the framework's own and nobody else's.** `.studyforge` is
#: this tool's, and `.git` holds the declaration this module now reads rather
#: than guesses at. ⚠️ **Beneath the root neither is the framework's**: a
#: nested `.studyforge` is material, and a nested `.git` is refused by name
#: (`RULE_NESTED_REPOSITORY`). ⚠️ **The archive root is not here** (`W248`): it
#: is skipped at the corpus root only, and `membership` refuses each file
#: beneath it that is not an archive member. A source's own nested `archive/`
#: is material.
#: Two more names once sat here —
#: `node_modules` and `__pycache__` — and they were the framework knowing about
#: two ecosystems it was told nothing about (R1). A list of other people's
#: build directories is wrong for the first corpus that uses a third ecosystem,
#: and right for the second two only by luck.
SKIP_DIRS = (".git", ".studyforge")

#: How long git is given to answer. ⚠️ A validator that hangs is worse than one
#: that says it could not check.
IGNORE_TIMEOUT = 30


def check_unclassified(walk: Walk) -> Iterator[Finding | Unchecked]:
    """Refuse a source file the manifest classifies as neither in nor out.

    ⛔ **Silence is the double ingest.** A file matching none of `content`'s
    three states is *unclassified*, and an unclassified file is refused rather
    than guessed at — one corpus ships per-unit files beside whole-series
    aggregates that are digest-identical concatenations of them, so a glob
    that swept both would read every unit twice and nothing would complain.

    ⚠️ **A file matched by both `include` and `not_material` is refused under
    its own rule id** — that is two glob authors contradicting each other, and
    picking a winner would decide by precedence what nobody declared.

    ⭐ `ContentPolicy.classify` does no I/O by design. Enumerating the root is
    this function's half of that split.
    """
    if walk.manifest is None:  # pragma: no cover - the walk stops without one
        return
    scan = source_files(walk.root)
    for path in scan.generated:
        where = walk.relative(path)
        if walk.manifest.content.classify(where) in (
            Classification.INCLUDED,
            Classification.CONTESTED,
        ):
            yield Finding(
                RULE_CONTESTED,
                where,
                "a build writes this path, and the manifest includes it as material. "
                "Neither is guessed: one would read generated output as the material, the "
                "other would let a build overwrite the material. Narrow the 'include' "
                "pattern, or move the material.",
            )
    for store in scan.stores:
        yield Finding(
            RULE_NESTED_REPOSITORY,
            walk.relative(store),
            "is another repository's store inside this corpus — a vendored repository or "
            "a submodule checkout. Its history is not material and is not read, and this "
            "repository's ignore rules do not answer for another repository's files. It "
            "is refused, not skipped: move that repository out of the corpus root, or "
            "declare its directory as output in this repository's ignore rules.",
        )
    if not scan.files:
        yield Unchecked(
            RULE_UNCLASSIFIED,
            ".",
            "no source material is present beside the archive, so there is nothing to classify",
        )
        return
    if not scan.planned:
        yield Unchecked(
            RULE_UNCLASSIFIED,
            ".",
            "`studyforge plan` refused this corpus, so what a build writes here could not be "
            "told from material. This corpus's own generated pages and media, if any, are "
            "reported below as unclassified rather than recognised. Run the plan to see why.",
        )
    if not scan.consulted:
        # ⛔ The walk stands and the report says so. A half-applied ignore rule
        # is the half-present source tree this package's docstring refuses.
        yield Unchecked(
            RULE_IGNORE_DECLARATION,
            ".",
            "the repository's own declaration of what is generated output could not "
            "be read — this corpus root is not a git working tree, or git is not "
            "installed. Every file beside the archive was scanned as material, so "
            "generated output is reported below as unclassified rather than skipped.",
        )
    read = _read_by_origins(walk)
    for path in scan.files:
        where = walk.relative(path)
        classification = walk.manifest.content.classify(where)
        if classification is Classification.UNCLASSIFIED:
            yield Finding(
                RULE_UNCLASSIFIED,
                where,
                "matches no 'include' pattern, no 'exclude' entry and no "
                "'not_material' glob. A file the manifest does not classify is not "
                "ingested and not refused — it is simply unaccounted for, which is "
                "how a corpus is read twice or not at all.",
            )
        elif classification is Classification.CONTESTED:
            yield Finding(
                RULE_CONTESTED,
                where,
                "matches an 'include' pattern and a 'not_material' glob at once, and "
                "the manifest does not say which holds. Neither answer is guessed: "
                "one would drop material the reader was promised, the other would "
                "read the repository's own scaffolding aloud. Narrow one of the two "
                "patterns, or move this file to 'exclude' with its reason.",
            )
        elif classification is Classification.INCLUDED and read and path not in read:
            yield Finding(
                RULE_INCLUDED_UNREAD,
                where,
                "matches an 'include' pattern and no unit's 'origin' names it, so no unit reads "
                "it: material the corpus carries twice or not at all (C2). Name it as a unit's "
                "origin, or move it to 'exclude' with its reason.",
            )


def _read_by_origins(walk: Walk) -> frozenset[Path]:
    """Every file a unit `origin` names; ⛔ EMPTY when that cannot be judged.

    Empty when no named file is on disk (`origin-missing`'s answer) or a map did not parse.
    """
    maps = [held.container for held in walk.containers]
    named = {walk.root / u.origin for c in maps for u in c.units if u.origin}
    if any(item.container is None for item in walk.refused):
        return frozenset()
    return frozenset(named) if any(path.is_file() for path in named) else frozenset()


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
    #: can print the population it judged (`W242`).
    generated: tuple[Path, ...] = ()
    #: ⛔ False when the plan refused: nothing was recognised, which is not
    #: the same as nothing having been generated.
    planned: bool = True
    #: ⛔ Each nested repository store the repository does not declare as
    #: output, refused by name (`W259`). Its contents are never in `files`.
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
    walked, stores = _walk(root)
    recognised = _generated_output(root, walked)
    generated = tuple(path for path in walked if recognised and path in recognised)
    candidates = [path for path in walked if not recognised or path not in recognised]
    declared = repository_ignores(root, candidates + stores)
    planned = recognised is not None
    if declared is None:
        return Scan(
            tuple(candidates),
            consulted=False,
            generated=generated,
            planned=planned,
            stores=tuple(stores),
        )
    files = tuple(path for path in candidates if path not in declared)
    refused = tuple(store for store in stores if store not in declared)
    return Scan(files, consulted=True, generated=generated, planned=planned, stores=refused)


def _generated_output(root: Path, candidates: list[Path]) -> frozenset[Path] | None:
    """Which of `candidates` a build of this corpus writes, by the plan's own enumeration.

    ⛔ **The plan's answer, never a list here** (Ruling 99, `W242`). A plan line
    ending in `/` is a directory whose contents a build or `narrate` fill, and
    every other line is a file — the plan's printed distinction, which
    `generate.footprint` reads the same way. ⚠️ Unlike a footprint, a unit's
    audio directory IS a prefix here: narrate's clips are generated media
    whoever wrote them.

    ⛔ **`None` when the plan refused.** An incomplete enumeration recognises
    nothing, and the caller says so.

    ⚠️ **The import is deferred, for `generate.footprint`'s reason:** `cli`
    imports the dispatcher, which imports this package. The enumeration living
    inside a command is `W202` item 5's finding.
    """
    from studyforge.cli.plan import plan_for

    plan = plan_for(root)
    if plan.refusals:
        return None
    files = {root / path for path in plan.paths if not path.endswith("/")}
    directories = [root / path.rstrip("/") for path in plan.paths if path.endswith("/")]
    return frozenset(
        path
        for path in candidates
        if path in files or any(path.is_relative_to(directory) for directory in directories)
    )


def _walk(root: Path) -> tuple[list[Path], list[Path]]:
    """Every file under `root` that is not the framework's own writing, and every nested store.

    ⛔ **`SKIP_DIRS` is asked of the first part only** (`W259`): a nested
    `.studyforge` is walked like any directory. A nested `.git`, directory or
    gitfile, is returned as a store and never entered.
    """
    found: list[Path] = []
    stores: set[Path] = set()
    for path in sorted(root.rglob("*")):
        parts = path.relative_to(root).parts
        if parts[0] in SKIP_DIRS:
            continue
        if len(parts) > 1 and parts[0] == ARCHIVE_DIRNAME:
            # ⛔ Not silent: `membership` accounts for every file here (`W248`).
            continue
        if REPOSITORY_STORE in parts:
            stores.add(root.joinpath(*parts[: parts.index(REPOSITORY_STORE) + 1]))
            continue
        if not path.is_file():
            continue
        if len(parts) == 1 and parts[0] == "corpus.json":
            continue
        found.append(path)
    return found, sorted(stores)


def repository_ignores(root: Path, candidates: list[Path]) -> frozenset[Path] | None:
    """Which of `candidates` the repository declares as generated output.

    ⭐ **Public because it is the ONE ignore reader (`W28`), and a second
    caller imports it rather than keeping a list** (`W257`): the scaffolded
    `test_emit` asks it which directories a working copy leaves behind.

    ⛔ **Git's own answer, never a reimplementation of it.** Ignore rules have
    precedence, negation, per-directory files, an index that makes a tracked
    file un-ignorable and a user's global configuration. A framework that
    reproduced four of those five would be wrong on the fifth, silently, in
    somebody else's repository.

    ⛔ **`None` means "not answered", and it is not the same as "nothing is
    ignored".** Fail-open is what this task exists to remove: the caller turns
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
        # one input guaranteed to carry a home directory (`W257`, the census).
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
