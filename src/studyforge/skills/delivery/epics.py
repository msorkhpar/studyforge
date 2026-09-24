r"""Reading epic documents, and the document that declares the order they run in.

**What it does.** Turns markdown into the data `capability` indexes: one
`Epic` per document, one `Sequence` for the declared milestone order. It is
handed text and gives back data, so the caller names the documents. ⭐ Each
capability carries its `Owns` cell **verbatim** and each epic its preamble,
which is everything any document says about whose work a row is (`W92`) —
⛔ carried, never read: the reading is `components`'.

**How you use it.**

    from studyforge.skills.delivery import read_epic, read_epics, read_sequence

    sequence = read_sequence("README.md", task_index_text)
    epics = read_epics(documents)   # every document, naming every one that fails
    one = read_epic("E05.md", text) # or one at a time

**Depends on.** `re` and this package's `capability` and `refusal`. ⛔ Nothing
else, ever — and in particular **not the filesystem**: a module that went
looking for `docs/tasks/` would be a framework module that knows where a plan
lives, and the next repository's plan does not live there.

## ⭐ The parse is mechanical, and the mechanism is the point

⛔ **A task is a `###` heading whose next non-blank line declares a
milestone.** Nothing else is a task — not a carried ruling, not a revision
note, not a section of prose — and the rule is *adjacency*, never a list of
headings to skip. ⚠️ A list would need an entry every time somebody wrote a
new kind of subsection, and the entry nobody adds is the row that vanishes.

⛔ **A row whose milestone is a dash is CANCELLED and is not a capability**,
and it is counted rather than dropped silently: a generator that quietly
discards input is one nobody can check. ⛔ **Only a dash cancels** (W247).

⛔ **The milestone order is READ from the document that already declares it** —
its `### M<n> — <name>` sections, in the order they appear — named by the
caller exactly as the epics are, and never retyped by the next repository
(R19).

## ⛔ Every unreadable row is named, and so is every unreadable document

⚠️ **Ruling 188, at the two places this module iterates.** A walk over a
document that stopped at its first malformed row, or a walk over thirteen
documents that stopped at the first unreadable one, tells its reader how much
is wrong only by being run again — and each run is the whole generation.
⭐ **So both loops gather and refuse once**, and `read_epics` is the reason
`read_epic` may still be called on its own: the single-document call is the
unit, and the population is assembled around it rather than inside it.

## ⚠️ This module names no source and reads no source

⛔ R1: it parses whatever documents it is given. R20: it never sends a reader
to a path inside the extraction source.

## ⛔ Why this is not in `capability.py` (`W94`, Ruling 261)

⭐ **The seam is the question asked.** This module answers *what does this
document say*; `capability` answers *when does capability X land*. ⚠️ They were
one module until the collect-then-enumerate form had to grow both of this
one's loops, at which point that module stood at R11's ceiling exactly — and
R11's remedy is a split at a named seam, never a trim.

⭐ **`W92` cut the same module at the SAME line and named the halves the other
way round** — its `capability` was this reading and its `index` was the index.
⚠️ **One cut, two namings, and the two were collapsed rather than stacked**:
this file is the reading half under `W94`'s name, and `components` is
the second READER on this side of that one cut — the pin document's, not the
epics'. ⛔ **Nothing was cut a third time to avoid deciding.**
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from studyforge.skills.delivery.capability import Capability, Epic, IndexRefused, Sequence
from studyforge.skills.delivery.refusal import one_or_all

#: A task heading: `### <ID> — <what>`. The id shapes are the two this
#: project mints — an epic prefix with a number and an optional letter
#: (`AB-35`, `CD-05a`), which is `tools.quality.config.ROW_ID`'s first half.
#: ⛔ Re-declared rather than imported: `src/` may not import `tools/`.
_HEADING = re.compile(r"^###\s+([A-Z]{2,4}-[0-9]{1,3}[a-z]?)\s+—\s+(.+?)\s*$")

#: Any `###` heading at all, so the walk can tell "not a task" from
#: "a task whose heading is malformed" instead of conflating them.
_ANY_HEADING = re.compile(r"^###\s+\S")

#: The declaration line that makes a heading a task.
_DECLARATION = re.compile(r"^\*\*Milestone\*\*")

#: ⛔ THE milestone id, any width (W247): a one-digit shape read `M10` as cancelled.
MILESTONE_ID = r"M[0-9]+"

#: The milestone inside it — an id, or the dash that cancels — allowing the bold.
_MILESTONE = re.compile(rf"^\*\*Milestone\*\*\s*\**\s*({MILESTONE_ID}\b|—)")

#: A milestone's own section in the order document: `### M6 — The first corpus reads`.
_SECTION = re.compile(rf"^###\s+({MILESTONE_ID})\s+—\s+\S")

#: What a task waits on, up to the next field.
_DEPENDS = re.compile(r"\*\*Depends on\*\*\s*(.*?)(?:·|$)")

#: The epic's own title: `# E05 — Serving and execution`.
_AREA = re.compile(r"^#\s+(E[0-9]{2})\s+—\s+(.+?)\s*$")

#: The `Owns` cell, which runs to the next declared field or the end of the
#: block. ⛔ Kept VERBATIM and never interpreted here (`W92`): what it means
#: about a row's side is `components`' reading, and this module has no opinion.
_OWNS = re.compile(r"\*\*Owns\*\*\s*(.*?)(?:\*\*Context\*\*|$)", re.S)

#: The decoration this project writes into headings. A capability's name stops
#: at the first one — `Delivery planning ⭐ THE PRODUCT OWNER…` names a
#: capability called *Delivery planning*, and the shouting is emphasis.
_DECORATION = re.compile(r"\s*[⭐⛔⚠✅]")

#: How many lines after a heading the declaration may sit. ⚠️ Two blank-line
#: styles are in use and one row carries a lead sentence; three is what covers
#: every task in the tree with no room for a coincidence.
_LOOKAHEAD = 3

#: ⛔ What a citable document name may NOT contain. A `name` is how a document
#: is cited in a refusal, so it is checked to be a bare filename **before**
#: anything quotes it — after which quoting it cannot put a home directory in
#: a log (R7). ⭐ That is the same construction `where=path.name` uses
#: everywhere else in this tree, arriving at a parameter instead of a `Path`.
_NOT_IN_A_NAME = ("/", "\\")


def _citable(name: str) -> None:
    """Refuse a document name that is not a bare filename, before anything quotes it."""
    if not name.strip() or any(part in name for part in _NOT_IN_A_NAME):
        raise IndexRefused(
            "a document is cited by a bare filename, never by a path — ⛔ and the "
            "offending value is withheld rather than quoted, because a refusal that "
            "echoed it would put an unvetted path in a log (R7)"
        )


def _clean(what: str) -> str:
    """Take the capability's name, with the heading's shouting removed."""
    stopped = _DECORATION.split(what, maxsplit=1)[0].strip()
    return stopped or what.strip()


def _dependencies(line: str) -> tuple[str, ...]:
    """Read the task ids a declaration line says this one waits on."""
    match = _DEPENDS.search(line)
    if match is None:
        return ()
    body = match.group(1).replace("*", "").strip()
    names = [name.strip() for name in body.split(",")]
    return tuple(name for name in names if name and name != "—")


def _block(lines: list[str], start: int) -> list[str]:
    """Return the declaration following the heading at `start`, and the lines under it.

    ⚠️ The declaration is not one line (`W92`). `**Milestone**` opens it and
    `**Owns**` usually sits on the next, so a walk that read only the first
    line could never see the cell that says whose work the row is.
    """
    for offset, line in enumerate(lines[start + 1 : start + 1 + _LOOKAHEAD], start + 1):
        if not line.strip():
            continue
        if not _DECLARATION.match(line):
            return []
        block: list[str] = []
        for following in lines[offset:]:
            if not following.strip():
                break
            block.append(following)
        return block
    return []


def _owns(block: list[str]) -> str:
    """Take the `Owns` cell verbatim, or the empty string when the row declares none."""
    match = _OWNS.search(" ".join(block))
    return match.group(1).strip() if match else ""


def read_sequence(name: str, text: str) -> Sequence:
    """Read the order milestones run in from the document that declares it.

    ⛔ The order is the order its `### M<n> — <name>` sections appear in, and
    never the order their ids sort to. Refuses a document that declares no
    milestone, and one that declares a milestone twice: a second section gives
    one gate two places, and *when* stops having an answer.
    """
    _citable(name)
    declared = [match.group(1) for line in text.splitlines() if (match := _SECTION.match(line))]
    if not declared:
        raise IndexRefused(f"{name}: no `### M<n> — <name>` section, so it declares no order")
    twice = tuple(dict.fromkeys(item for item in declared if declared.count(item) > 1))
    if twice:
        raise IndexRefused(f"{name}: {', '.join(twice)} declared twice, so its place is ambiguous")
    return Sequence(name=name, milestones=tuple(declared))


def read_epic(name: str, text: str) -> Epic:
    """Read one epic document into its capabilities.

    `name` is how the document should be cited — ⛔ a **bare filename**, which
    is checked here rather than trusted, so that every refusal below may quote
    it without risk of putting a path in a log (R7). ⛔ Also refuses a document
    with no `# E<nn> — <area>` title: an index whose rows have no area is an
    index nobody can scan.

    ⛔ **Every unreadable row is named, not the first one** (Ruling 188): the
    walk gathers and the refusal is raised once, after it.
    """
    _citable(name)
    lines = text.splitlines()
    titled = next((_AREA.match(line) for line in lines if _AREA.match(line)), None)
    if titled is None:
        raise IndexRefused(f"{name}: no `# E<nn> — <area>` title, so its rows have no area")
    epic, area = titled.group(1), _clean(titled.group(2))

    found: list[Capability] = []
    cancelled: list[str] = []
    refusals: list[str] = []
    for position, line in enumerate(lines):
        if not _ANY_HEADING.match(line):
            continue
        block = _block(lines, position)
        if not block:
            continue
        declaration = block[0]
        heading = _HEADING.match(line)
        if heading is None:
            refusals.append(
                f"{name} line {position + 1}: a task heading declares a milestone and "
                "carries no id. ⛔ The line is not quoted: it is caller text"
            )
            continue
        milestone = _MILESTONE.match(declaration)
        if milestone is None:
            refusals.append(
                f"{name} line {position + 1}: {heading.group(1)} declares a milestone that is "
                "neither `M<n>` nor a dash — refused, never counted as cancelled (W247)"
            )
            continue
        if milestone.group(1) == "—":
            cancelled.append(heading.group(1))
            continue
        found.append(
            Capability(
                id=heading.group(1),
                what=_clean(heading.group(2)),
                milestone=milestone.group(1),
                area=area,
                epic=epic,
                depends_on=_dependencies(declaration),
                owns=_owns(block),
            )
        )
    if refusals:
        raise IndexRefused(one_or_all(refusals))
    return Epic(
        epic=epic,
        area=area,
        capabilities=tuple(found),
        cancelled=tuple(cancelled),
        preamble=text.split("\n### ", 1)[0],
    )


def read_epics(documents: Iterable[tuple[str, str]]) -> tuple[Epic, ...]:
    """Read every `(name, text)` document, ⛔ naming EVERY one that cannot be read.

    ⚠️ **This is the call boundary Ruling 188's population is derived across**
    (`W94`). Reading thirteen epic documents through a generator that stops at
    the first unreadable one tells the reader nothing about the other twelve,
    and the shape of that refusal — correct inside `read_epic`, first-witness
    once a loop is wrapped around it — is invisible to any instrument that
    looks at one function at a time.
    """
    found: list[Epic] = []
    refusals: list[str] = []
    for name, text in documents:
        try:
            found.append(read_epic(name, text))
        except IndexRefused as refused:
            refusals.append(str(refused))
    if refusals:
        raise IndexRefused(one_or_all(refusals))
    return tuple(found)
