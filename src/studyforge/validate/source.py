r"""The two checks that read the material, not only what the adapter wrote.

**What it does.** Refuses a file the manifest classifies as neither included
nor excluded, and — the check this task exists for — **counts a structural
feature directly in the raw source and compares it against the archive**.

**How you use it.** `check_unclassified(walk)` and `check_completeness(walk)`,
both yielding `Finding`s and `Unchecked`s like every other check.

**Depends on.** `corpus.manifest` for the classification, `archive.blocks` for
what a heading is, `validate.corpus`, `validate.report`.

## A completeness check counts something the parser did not produce

⛔ **Two readings from the same parser are not two readings.** A digest
computed from the blocks and compared against the blocks answers *"was this
corrupted after we wrote it?"*. It cannot answer *"did the adapter read
everything the source contained?"* — the two readings come from the same
place, so a construct the parser never recognised is absent from both, the
counts agree, and nothing raises.

⚠️ The extraction source met exactly this shape: a guard compared section
containers against regex-derived pairs from the same regex family, a section
written in a shape neither recognised was missing from both, `5 == 5`, and
five lessons lost a section in one wave with nothing failing.

⚠️ **studyforge is more exposed than that, not less.** The extraction source
has two independent readings of every lesson and refuses a disagreement
between them. An adapter reading Markdown directly has **one**. And C3
establishes the realistic failure: raw HTML in real Markdown yields a short,
well-formed, entirely plausible unit rather than an error.

⭐ **So this check does not use the Markdown reader.** It counts ATX heading
lines with a regex of its own, outside fenced code blocks, and compares the
number against the archive's `headings` count. A check that can only fail when
the parser already failed loudly is not a check.

## Where the source is, and what happens when it is not there

⛔ **All or nothing, and half is a failure.** If **no** origin the container
maps name is on disk, the source tree is absent and every source-dependent
claim is reported `Unchecked` — loudly, counted, in the output (R6's sibling).
If **some** are present, all must be: a half-present source is exactly where a
short read hides, and a per-file skip would discount precisely the file that
went missing.

⭐ The alternative — failing whenever the source is absent — was rejected
because an archive is a shippable artifact on its own, and `validate` is the
adapter's definition of done for *the archive* (R2). What it may not do is
pretend it checked.

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

⛔ **A root that is not a git working tree gets the old walk and an
`Unchecked`** (`ignore-declaration`), never a guess. Same rule as the absent
source tree above, for the same reason: a half-applied ignore rule is a
half-present input, and the dangerous half is the one that looks clean.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from studyforge.corpus.manifest import Classification
from studyforge.validate.corpus import ARCHIVE_DIR, Walk
from studyforge.validate.report import Finding, Unchecked

RULE_UNCLASSIFIED = "unclassified"
RULE_SHORT_READ = "short-read"
RULE_ORIGIN_MISSING = "origin-missing"

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

#: An ATX heading, counted **outside** fenced code. ⛔ Deliberately not the
#: Markdown reader's: this number exists to disagree with the parser, so it
#: may not come from it.
HEADING_LINE = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")

#: A fence opening or closing. ⚠️ Fence awareness is the whole difficulty: a
#: `#` inside a code block is a comment in half the languages this framework
#: will meet, and counting it would make the check cry wolf on correct output.
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")

#: Directories a source scan never descends into. ⚠️ The archive is generated
#: output living inside the corpus root; sweeping it would classify the
#: adapter's own writing as unclassified material.
#:
#: ⛔ **These three are the framework's own and nobody else's.** `archive` is
#: R2's, `.studyforge` is this tool's, and `.git` holds the declaration this
#: module now reads rather than guesses at. Two more names once sat here —
#: `node_modules` and `__pycache__` — and they were the framework knowing about
#: two ecosystems it was told nothing about (R1). A list of other people's
#: build directories is wrong for the first corpus that uses a third ecosystem,
#: and right for the second two only by luck.
SKIP_DIRS = (ARCHIVE_DIR, ".git", ".studyforge")

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
    if not scan.files:
        yield Unchecked(
            RULE_UNCLASSIFIED,
            ".",
            "no source material is present beside the archive, so there is nothing to classify",
        )
        return
    if not scan.consulted:
        # ⛔ The walk stands and the report says so. A half-applied ignore rule
        # is the half-present source tree this module's docstring refuses.
        yield Unchecked(
            RULE_IGNORE_DECLARATION,
            ".",
            "the repository's own declaration of what is generated output could not "
            "be read — this corpus root is not a git working tree, or git is not "
            "installed. Every file beside the archive was scanned as material, so "
            "generated output is reported below as unclassified rather than skipped.",
        )
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


def check_completeness(walk: Walk) -> Iterator[Finding | Unchecked]:
    """Compare a heading count taken from the raw source against the archive.

    ⛔ The count on the left is produced by this module's own regex and the
    count on the right by the adapter's parser. That is the whole point: two
    readings from one parser agree by construction.
    """
    if walk.manifest is None:  # pragma: no cover - the walk stops without one
        return
    origins = _origins(walk)
    present = [origin for origin in origins if origin[1].exists()]
    if not origins:
        yield Unchecked(
            RULE_SHORT_READ,
            ".",
            "no container map declares an 'origin', so there is no source file to count against",
        )
        return
    if not present:
        yield Unchecked(
            RULE_SHORT_READ,
            ".",
            f"none of the {len(origins)} declared origin file(s) is present, so the "
            f"source tree is absent and no unit's completeness was checked",
        )
        return
    for where, path, recorded in origins:
        if not path.exists():
            # ⛔ Half a source tree is a failure, not a discount: a per-file
            # skip would excuse precisely the file that went missing.
            yield Finding(
                RULE_ORIGIN_MISSING,
                where,
                "names an origin that is not on disk, while other origins in this "
                "corpus are. Either the whole source tree is beside the archive or "
                "none of it is; half of it is where a short read hides.",
            )
            continue
        yield from _compare(where, path, recorded)


def _compare(where: str, path: Path, in_archive: int) -> Iterator[Finding]:
    text = _read(path)
    if text is None:
        return
    in_source = count_headings(text)
    if in_source != in_archive:
        yield Finding(
            RULE_SHORT_READ,
            where,
            f"its source carries {in_source} heading line(s) and the archive records "
            f"{in_archive} heading block(s). The digest cannot see this: it is taken "
            f"over what the parser produced, so a construct the parser skipped is "
            f"missing from both sides of it.",
        )


def count_headings(text: str) -> int:
    """Count ATX heading lines outside fenced code.

    ⚠️ **Fence-aware, and that is not decoration.** A `#` at the start of a
    line inside a fence is a comment in Python, Ruby, shell and YAML; counting
    those would make this check fire on correct output, and a check that fires
    on correct output is a check somebody turns off.
    """
    count = 0
    fence: str | None = None
    for line in text.splitlines():
        marker = FENCE.match(line)
        if marker is not None:
            if fence is None:
                fence = marker.group(1)[0]
            elif marker.group(1)[0] == fence:
                fence = None
            continue
        if fence is None and HEADING_LINE.match(line):
            count += 1
    return count


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
    walked = _walk(root)
    declared = _declared_output(root, walked)
    if declared is None:
        return Scan(tuple(walked), consulted=False)
    return Scan(tuple(path for path in walked if path not in declared), consulted=True)


def _walk(root: Path) -> list[Path]:
    """Every file under `root` that is not the framework's own writing."""
    found: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in parts[:-1]) or parts[0] in SKIP_DIRS:
            continue
        if len(parts) == 1 and parts[0] == "corpus.json":
            continue
        found.append(path)
    return found


def _declared_output(root: Path, candidates: list[Path]) -> frozenset[Path] | None:
    """Which of `candidates` the repository declares as generated output.

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
    payload = "\0".join(path.relative_to(root).as_posix() for path in candidates)
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


def _origins(walk: Walk) -> list[tuple[str, Path, int]]:
    """Return `(unit key, origin path, headings recorded)` per **unit**, not document.

    ⚠️ **Summed across the unit's documents, deliberately.** One origin file is
    one unit, and a unit may hold several archive documents — `depth1`'s third
    unit holds two lessons. Comparing one document against the whole file would
    report a short read on every multi-document unit in the corpus, which is
    the shape of a check that gets switched off.
    """
    totals: dict[tuple[str, int], int] = {}
    origins: dict[tuple[str, int], Path] = {}
    for unit in walk.units:
        n = unit.document.get("unit")
        declared = next((d for d in unit.container.units if d.n == n), None)
        if declared is None or declared.origin is None:
            continue
        key = (unit.container.address.unit_key(declared.n), declared.n)
        totals[key] = totals.get(key, 0) + (unit.document.get("counts") or {}).get("headings", 0)
        origins[key] = walk.root / declared.origin
    return [(key[0], origins[key], totals[key]) for key in sorted(totals)]


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:  # pragma: no cover - reported by the walk
        return None


CHECKS = (check_unclassified, check_completeness)
