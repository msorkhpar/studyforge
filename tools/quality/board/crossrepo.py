"""`W403`: a cross-repo task DECLARES BOTH HALVES, and the SIBLING half is read AT THE PIN.

**What it does.** Reads the `<!-- crossrepo -->` block of `docs/tasks/CROSSREPO.md` — one row
per task whose work lands in TWO repositories — and answers, for each, whether BOTH halves
are landed: the framework half against the release branch of this checkout, and ⭐ **the
sibling half against that component's PINNED commit in `workspace.json`, never against its
working tree.**

**How you use it.** `read_declaration(root)` returns a `Declaration` (`read(text)` is its
text half); `judge(root, declaration, release)` returns `board.verdict.Verdict` — Ruling
216's THREE answers, not two. ⛔ **`corroborate` calls both and folds the answer into its
exit code; nothing in `tools.quality.CHECKS` imports this**: the sibling half is a git
reading and the floor may not shell out to git (`board.md`, ruled round 50).

**Depends on.** `board.register` and `board.verdict` for the board's cell grammar and its
three answers, `board.observation` for the vocabulary of a cell that declares NOTHING, and
`tools.workspace` for the pin file and its git readings.

## ⛔ The defect, measured by the register on 2026-09-20 (`BOARD-ARCHIVE.md`, PO round 128)

⚠️ **`TC-05`'s framework half merged in round 127 and its handoff landed here, while its
sibling's `main` checkout sat in an ABANDONED CONFLICTED MERGE** — `MERGE_HEAD` present,
every file staged, none committed. ⛔ **So `consuming.json`, that task's entire deliverable
and the seam's whole definition (R2), existed on NO COMMITTED REF** — and the task was
recorded MERGED, and step 7.3 recorded it, on a reading nobody could have taken. ⭐ **A
cross-repo task has two halves and the register read one.** ⛔ **The remedy is not a habit:**
an undeclared half cannot be read, and a half read off a working tree is not a reading
anything else gets back.

## ⛔ Why the sibling half is read at the PIN and never at `HEAD`

⚠️ **`python3 -m tools.workspace verify` read GREEN, exit `0`, through all of it**: it
compares `HEAD` to the pin and is silent about what the tree around `HEAD` is doing. ⭐ **The
pin is the only ref that is a FACT ABOUT THE PROJECT** — committed here, travelling with the
repository, resolved by a rebuild — ⛔ **while a working tree is a fact about one disk at one
minute**, which is what made the missing half read as present. ⭐ So a half is LANDED when
the component's PINNED commit REACHES the declared ref. ⚠️ **`W404` is building the same
reading for the other sibling readers; this module states what it needs rather than waiting
on it, and the register converges them.**

## ⛔ The three answers, and the third is why this can be trusted at all

⭐ `CORROBORATED` when both halves are declared and reached; ⛔ `REFUTED`, naming WHICH half
and WHICH component, when one is undeclared, unresolvable or unreached; ⚠️ `NOT_ANSWERABLE`
when the component is not there to be asked — ⛔ **never a pass.**

⛔ **That third state is the whole reason `observation.py` excluded a cross-repo row BY NAME
(`STAND_INS`) rather than reading across the seam:** an instrument that shelled into a
sibling checkout would be GREEN wherever that sibling is absent, which is the PASS reading
from an empty population (Ruling 191). ⚠️ **And the absence names the CONTAINER, never the
worktree** (Ruling 248(a)): the pinned image mounts one directory (`FND-03`), while a linked
worktree DOES reach the siblings through `--git-common-dir`.

## ⛔ Why the declaration is a SIBLING OF THE BOARD and not a block inside it

⚠️ **MEASURED at `778e618a`, before this file was placed: the board is 112,337 bytes against
112,416 allowed — 79 bytes of headroom**, and the smallest well-formed block is an order of
magnitude more. ⛔ **Raising the term is refused by Ruling 271**: `board-size`'s allowance
grows with the register ids and the delimited observation and scheduled rows, and a new block
earns nothing in any of the three. ⭐ **What it costs, said rather than hidden:** a reader of
`BOARD.md` alone does not see this file, so it is named in `CROSSREPO` below and in
`docs/conventions/board.md` — and the day the board has room, a POINTER belongs there too.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from tools.quality.board.observation import ABSENT as DECLARES_NOTHING
from tools.quality.board.register import cells, normalised
from tools.quality.board.verdict import Answer, Verdict, tokens
from tools.workspace import PIN_FILENAME, Component, PinError, git, head_of, holds, is_ancestor
from tools.workspace import read as pins
from tools.workspace.__main__ import DEV_CONTAINER, workspace_root

#: ⛔ **Where a task landing in TWO repositories declares BOTH its halves.** ⚠️ **Named here
#: and not beside `BOARD` in `register.py`, which is at 400/400**: this is its one reader.
CROSSREPO = "docs/tasks/CROSSREPO.md"

#: ⛔ The declaration is DELIMITED — the `<!-- inflight -->` pattern, reused rather than
#: reinvented (`board.md`, ruled round 49). ⚠️ A population that grows by INFERENCE moves the
#: moment somebody writes an ordinary table, and this board already paid for that once.
CROSSREPO_OPEN = "<!-- crossrepo -->"
CROSSREPO_CLOSE = "<!-- /crossrepo -->"

#: ⭐ The three states a declaration can be in, `offices.py`'s vocabulary reused. ⛔ Only
#: `DECLARED` answers, and ⚠️ **a DECLARED and EMPTY block is a real answer** — *this board
#: declares no cross-repo task* — which is the distinction Ruling 191(a) exists to keep.
ABSENT = "ABSENT"
UNREADABLE = "UNREADABLE"
DECLARED = "DECLARED"

#: ⛔ The four roles a declaring header must carry, read from the header and never from a
#: position (`observation._columns`'s move): the PO may reorder or rename the columns and
#: this still reads them, while an ordinary table cannot satisfy four roles by accident.
ROLES = ("task", "component", "framework", "sibling")

#: How much of a commit id a refusal prints. ⚠️ Enough to locate, never a path.
SHORT = 12


@dataclass(frozen=True)
class Entry:
    """One cross-repo task, as the board declares it — ⛔ BOTH halves or the row is refused."""

    line: int
    task: str
    component: str
    framework: str
    sibling: str

    @property
    def halves(self) -> tuple[str, ...]:
        """The halves this row DECLARES; ⛔ fewer than two is `W403`'s own defect."""
        return tuple(half for half in (self.framework, self.sibling) if half)


@dataclass(frozen=True)
class Declaration:
    """What the board's `<!-- crossrepo -->` block declares, INCLUDING that it did not read."""

    state: str
    entries: tuple[Entry, ...] = ()
    #: The line of the first declared block whose table declares no header, else `0`.
    line: int = 0


def declared(cell: str) -> str:
    """Return the one token a cell declares, or `""` where it declares NOTHING.

    ⭐ **The code span is the board's own idiom for a ref or a name** (`verdict.tokens`) and
    ⛔ **the negative vocabulary is `observation.ABSENT`'s** — `none`, `—`, a blank cell — so
    *a dash here* and *a ref here* cannot arrive as the same answer.
    """
    found = tokens(cell)
    if found:
        return found[0]
    return "" if normalised(cell).strip().lower() in DECLARES_NOTHING else normalised(cell).strip()


def _roles(line: str) -> dict[str, int] | None:
    """`{role: index}` when this header DECLARES all four roles, else `None`."""
    roles: dict[str, int] = {}
    for index, cell in enumerate(cells(line)):
        plain = normalised(cell).lower()
        for role in ROLES:
            if role in plain:
                roles.setdefault(role, index)
    return roles if set(ROLES) <= roles.keys() else None


def _entry(number: int, line: str, roles: dict[str, int]) -> Entry | None:
    """One data row against an already-declared header, or `None` if it is not one."""
    columns = cells(line)
    if len(columns) <= max(roles.values()) or set(columns[0]) <= set("-: "):
        return None
    return Entry(
        line=number,
        task=declared(columns[roles["task"]]),
        component=declared(columns[roles["component"]]),
        framework=declared(columns[roles["framework"]]),
        sibling=declared(columns[roles["sibling"]]),
    )


def read(text: str) -> Declaration:
    """Return the declaration: ⛔ ABSENT with no block, UNREADABLE when a block did not parse.

    ⭐ **The marker is matched as the WHOLE LINE**, as `observation.py` and `offices.py`
    match theirs, so prose that MENTIONS it declares nothing. ⚠️ **An unclosed block is judged
    at end-of-file**: a missing close marker must not make a declared block vanish.
    """
    entries: list[Entry] = []
    opened = unreadable = 0
    any_block = read_any = False
    roles: dict[str, int] | None = None
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped in (CROSSREPO_OPEN, CROSSREPO_CLOSE):
            if opened and not read_any and not unreadable:
                unreadable = opened
            opened = number if stripped == CROSSREPO_OPEN else 0
            any_block = any_block or bool(opened)
            roles, read_any = None, False
            continue
        if not opened:
            continue
        if not line.startswith("|"):
            roles = None
            continue
        if roles is None:
            roles = _roles(line)
            read_any = read_any or roles is not None
            continue
        found = _entry(number, line, roles)
        if found is not None:
            entries.append(found)
    if opened and not read_any and not unreadable:
        unreadable = opened
    if not any_block:
        return Declaration(ABSENT)
    if unreadable:
        return Declaration(UNREADABLE, tuple(entries), unreadable)
    return Declaration(DECLARED, tuple(entries))


def read_declaration(root: Path) -> Declaration:
    """Read the declaration this checkout files, or ABSENT when the file is not there.

    ⛔ **ABSENT is not *there are no cross-repo tasks*** — a missing file is this instrument
    failing to read this repository, which `judge` answers `NOT_ANSWERABLE`; ⭐ **a DECLARED
    and EMPTY block is the other answer** (Ruling 191(a), `W111`'s shape one table over).
    """
    path = root / CROSSREPO
    if not path.is_file():
        return Declaration(ABSENT)
    return read(path.read_text(encoding="utf-8"))


def _component(root: Path, name: str) -> tuple[Component | None, str]:
    """Resolve the pinned sibling `name`, or `(None, why not)` — ⛔ the pin file, never a guess."""
    try:
        recorded = pins(root)
    except PinError as error:
        return None, f"{PIN_FILENAME} did not read: {error}"
    for component in recorded:
        if component.name == name:
            if component.where != "sibling":
                return None, f"{PIN_FILENAME} records {name} as {component.where!r}, not a sibling"
            if not component.present:
                return None, f"{PIN_FILENAME} records {name} as not created yet"
            return component, ""
    return None, f"{PIN_FILENAME} pins no component called {name}"


def _reaches(where: Path, ref: str, of: str) -> bool | None:
    """Say whether `of` reaches `ref` in `where`; ⛔ `None` when git cannot resolve `ref`."""
    resolved = git(where, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if resolved.returncode != 0:
        return None
    return is_ancestor(where, ref, of)


def _refused(sentence: str) -> Verdict:
    """One REFUTED verdict, indented as this arm's lines are. ⛔ The answer is a FIELD."""
    return Verdict(Answer.REFUTED, (f"    ⛔ REFUTED: {sentence}",))


def _framework(root: Path, entry: Entry, release: str) -> Verdict | None:
    """Judge the half that lives HERE against the release branch; `None` when it is landed."""
    reached = _reaches(root, entry.framework, release)
    half = f"{entry.task}'s FRAMEWORK half {entry.framework}"
    if reached is None:
        return _refused(
            f"{half} is on NO COMMITTED REF of this repository — git resolves no commit for "
            f"it. ⚠️ A cross-repo task has two halves and this one is unread."
        )
    if not reached:
        return _refused(
            f"{half} is UNLANDED — {release} does not reach it. ⛔ The register may not "
            f"record this task merged while either half is unlanded (`W403`)."
        )
    return None


def _sibling(root: Path, entry: Entry, workspace: Path) -> Verdict | None:
    """Judge the half that lives in the COMPONENT, at its PIN; `None` when it is landed.

    ⛔ **Three refusals and they are different answers**: the component is not pinned
    (REFUTED), the component is not on disk (NOT ANSWERABLE — ⚠️ the container, never the
    worktree), and the declared ref is missing or unreached (REFUTED, which is `TC-05`).
    """
    component, why = _component(root, entry.component)
    if component is None:
        return _refused(f"{entry.task} names the component {entry.component} — {why}.")
    where = component.directory(workspace, root)
    pinned = component.commit[:SHORT]
    if head_of(where) is None or not holds(where, component.commit):
        return Verdict(
            Answer.NOT_ANSWERABLE,
            (
                f"    ⚠️ NOT ANSWERABLE: {entry.component} is not a checkout holding its "
                f"pinned commit {pinned} where this run can see it, so {entry.task}'s "
                f"sibling half has NO READING AT ALL (Ruling 216). ⛔ Not a pass. ⭐ The "
                f"pinned image mounts one directory (`FND-03`), so this reading is "
                f"host-verified — the CONTAINER is the reason, never the worktree "
                f"(Ruling 248(a)).",
            ),
        )
    reached = _reaches(where, entry.sibling, component.commit)
    half = f"{entry.task}'s SIBLING half {entry.sibling}"
    if reached is None:
        return _refused(
            f"{half} is on NO COMMITTED REF of {entry.component} — that component holds no "
            f"commit for it. ⭐ This is `TC-05`'s own reading: the deliverable was in a tree "
            f"and on no ref, and the task was recorded merged anyway."
        )
    if not reached:
        return _refused(
            f"{half} is UNLANDED in {entry.component} — the ref resolves, and the PINNED "
            f"commit {pinned} does not reach it. ⛔ The pin is the reading, never a working "
            f"tree (`W403`, `W404`)."
        )
    return None


def _judged(root: Path, entry: Entry, release: str, workspace: Path) -> Verdict:
    """One declared task, both halves — ⛔ the UNDECLARED half is refused before any git."""
    if len(entry.halves) < 2 or not entry.component or not entry.task:
        return _refused(
            f"at line {entry.line} this row declares {len(entry.halves)} half/halves, a task "
            f"{entry.task or 'nothing names it'} and a component "
            f"{entry.component or 'it does not name'}. ⛔ A task naming a sibling DECLARES "
            f"BOTH HALVES — an undeclared half is one nobody can read, which is how `TC-05` "
            f"closed (`W403`)."
        )
    for refusal in (_framework(root, entry, release), _sibling(root, entry, workspace)):
        if refusal is not None:
            return refusal
    return Verdict(
        Answer.CORROBORATED,
        (
            f"    ⭐ CORROBORATED: {entry.task} — the framework half {entry.framework} is "
            f"reached by {release}, and the {entry.component} half {entry.sibling} is reached "
            f"by that component's PINNED commit.",
        ),
    )


def _unanswerable(sentence: str) -> Verdict:
    """One NOT ANSWERABLE verdict for the whole declaration. ⛔ Never a pass."""
    return Verdict(Answer.NOT_ANSWERABLE, (sentence,))


def judge(
    root: Path, declaration: Declaration, release: str, workspace: Path | None = None
) -> Verdict:
    """Every declared cross-repo task against BOTH its halves — ⛔ three answers, never two.

    ⛔ **ABSENT and UNREADABLE are `NOT_ANSWERABLE`, not a pass** (Ruling 191(a)): the block
    is this board's contract, so its absence is this instrument failing to read THIS
    repository rather than a repository with no cross-repo task. ⭐ **A DECLARED and EMPTY
    block IS that second answer**, and it says so in its own sentence — the distinction the
    `<!-- inflight -->` block gained in `W111`.
    """
    label = f"  cross-repo halves ({CROSSREPO}):"
    entries = declaration.entries
    if declaration.state == ABSENT:
        return _unanswerable(
            f"{label} ABSENT — no {CROSSREPO_OPEN} block is declared here, so every task "
            f"whose other half lives in a sibling component is UNREAD. ⛔ NOT ANSWERABLE and "
            f"not a pass: the block is this board's contract (`board.md`, `W403`), and a "
            f"DECLARED and EMPTY one is how this repository says it has no cross-repo task."
        )
    if declaration.state == UNREADABLE:
        return _unanswerable(
            f"{label} UNREADABLE — the block at line {declaration.line} declares no header "
            f"carrying all of {list(ROLES)}. ⛔ A declared block that did not read is *I "
            f"could not answer*, never an empty one."
        )
    if not entries:
        return Verdict(
            Answer.CORROBORATED,
            (
                f"{label} DECLARED, READ, and carrying no row — ⭐ that is *this repository "
                f"has no cross-repo task*, which is a real answer and not an empty "
                f"population (Ruling 191(a)).",
            ),
        )
    if workspace is None:
        workspace = workspace_root(root)
        if os.environ.get(DEV_CONTAINER):
            return _unanswerable(
                f"{label} DECLARED with {len(entries)} entries, and this is the PINNED "
                f"IMAGE, which mounts one directory (`FND-03`) — so no sibling component can "
                f"be seen from in here and NO half is readable. ⛔ Exit NOT AUTHORITATIVE: "
                f"this reading is host-verified. ⚠️ The CONTAINER is the reason and never "
                f"the worktree (Ruling 248(a))."
            )
    verdicts = [_judged(root, entry, release, workspace) for entry in entries]
    answers = [verdict.answer for verdict in verdicts]
    refuted = answers.count(Answer.REFUTED)
    unanswerable = answers.count(Answer.NOT_ANSWERABLE)
    lines = [
        f"{label} DECLARED with {len(entries)} entries, each read at its component's PINNED "
        f"commit in {PIN_FILENAME} and never at a working tree.",
        *(line for verdict in verdicts for line in verdict.lines),
        f"  cross-repo: {refuted} of {len(verdicts)} declared cross-repo task(s) REFUTED and "
        f"{unanswerable} NOT ANSWERABLE. ⛔ A task naming a sibling declares BOTH halves, and "
        f"neither may be recorded merged while the other is unlanded (`W403`).",
    ]
    # ⛔ `NOT_ANSWERABLE` DOMINATES, as it does one layer up (Ruling 216): a run that could
    # not read a component is not a run that found it wrong, and folding the two together is
    # the FALSE REFUTATION this package refuses everywhere else.
    if unanswerable:
        return Verdict(Answer.NOT_ANSWERABLE, tuple(lines))
    return Verdict(Answer.REFUTED if refuted else Answer.CORROBORATED, tuple(lines))
