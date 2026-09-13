r"""The consumer-facing capability index — when does capability X become available.

**What it does.** Reads this repository's own epic documents and derives the
one map a planner needs about the framework — every capability, the milestone
that delivers it, and what it waits on. It renders that map as a document, and
the document is **generated**: a reviewer regenerates it and gets identical
bytes.

**How you use it.**

    from studyforge.skills.delivery import Index, read_epic, read_sequence

    sequence = read_sequence("README.md", task_index_text)
    index = Index.of((read_epic(name, text) for name, text in documents), sequence)
    index.milestone_of("SK-07")     # when a capability lands
    index.after("M4")               # everything a corpus finishing at M4 forgoes
    index.later("M5", than="M8")    # ⛔ in the declared order, never by id
    index.render()                  # the document

**Depends on.** `re` and `dataclasses`. ⛔ Nothing else, ever — and in
particular **not the filesystem**: this module is handed text and gives back
text, so the caller names the documents. A module that went looking for
`docs/tasks/` would be a framework module that knows where a plan lives, and
the next repository's plan does not live there.

## ⛔ Why this exists at all, measured on the filing side

⚠️ **An integration wrote a delivery plan by hand and derived the
capability→milestone map by reading thirteen epic documents** — which is
exactly the cost R14's context budgets exist to prevent, paid again by every
integration, and stale the moment an epic moves. ⭐ **Cost measured where it
was paid: 18 rows of a hand-written plan.**

⛔ **A hand-written index would be that same defect one layer up** (R19: the
consuming half is generated, never hand-authored), which is why this module is
a generator and not a table.

## ⭐ The parse is mechanical, and the mechanism is the point

⛔ **A task is a `###` heading whose next non-blank line declares a
milestone.** Nothing else is a task — not a carried ruling, not a revision
note, not a section of prose — and the rule is *adjacency*, never a list of
headings to skip. ⚠️ A list would need an entry every time somebody wrote a
new kind of subsection, and the entry nobody adds is the row that vanishes.

⛔ **A row whose milestone is a dash is CANCELLED and is not a capability**,
and it is counted rather than dropped silently: a generator that quietly
discards input is one nobody can check. ⛔ **Only a dash cancels** (W247).

## ⛔ Milestones run in a DECLARED order, which is not the order ids sort to

⚠️ **An id names a gate; it does not say when the gate comes**, and a plan can
be reordered without renaming one. Sorting ids answers *when does X land?* in
an order nobody decided, and drops a milestone no epic delivers anything at.
⭐ **So the order is READ from the document that already declares it** — its
`### M<n> — <name>` sections, in the order they appear — named by the caller
exactly as the epics are. ⛔ Never typed a second time here, and never retyped
by the next repository (R19): its order is read from its own document by the
same call. ⭐ **A declared milestone with no capability is printed, and says so.**

## ⚠️ This module names no source and reads no source

⛔ R1: it parses whatever documents it is given. R20: it never sends a reader
to a path inside the extraction source, and the document it renders carries no
such path — because the whole point of the index is that a consumer stops
having to go and look.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

#: A task heading: `### <ID> — <what>`. The id shapes are the two this
#: project mints — an epic prefix with a number and an optional letter
#: (`SF-35`, `FND-05a`), which is `tools.quality.config.ROW_ID`'s first half.
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

#: The decoration this project writes into headings. A capability's name stops
#: at the first one — `Delivery planning ⭐ THE PRODUCT OWNER…` names a
#: capability called *Delivery planning*, and the shouting is emphasis.
_DECORATION = re.compile(r"\s*[⭐⛔⚠✅]")

#: How many lines after a heading the declaration may sit. ⚠️ Two blank-line
#: styles are in use and one row carries a lead sentence; three is what covers
#: every task in the tree with no room for a coincidence.
_LOOKAHEAD = 3

#: The banner the rendered document opens with. ⛔ A generated document that
#: does not say so is a document somebody edits.
BANNER = "GENERATED by the delivery skill. Do not edit — regenerate."

#: What a declared milestone with no capability says, instead of vanishing.
EMPTY = (
    "⭐ **No epic document declares a capability at this milestone.** It is a gate "
    "in the declared order all the same, and a plan that waits on it waits here."
)

#: ⛔ What a citable document name may NOT contain. A `name` is how a document
#: is cited in a refusal, so it is checked to be a bare filename **before**
#: anything quotes it — after which quoting it cannot put a home directory in
#: a log (R7). ⭐ That is the same construction `where=path.name` uses
#: everywhere else in this tree, arriving at a parameter instead of a `Path`.
_NOT_IN_A_NAME = ("/", "\\")


class IndexRefused(Exception):
    """Raised when a document cannot be read as an epic, with the reason."""


@dataclass(frozen=True, slots=True)
class Capability:
    """One thing the framework will be able to do, and when."""

    id: str
    what: str
    milestone: str
    area: str
    epic: str
    depends_on: tuple[str, ...]

    def row(self) -> str:
        """Render as one row of the index's table."""
        waits = ", ".join(f"`{name}`" for name in self.depends_on) or "—"
        return f"| `{self.id}` | {self.what} | {self.area} | {waits} |"


@dataclass(frozen=True, slots=True)
class Epic:
    """One epic document, read as capabilities plus whatever was cancelled."""

    epic: str
    area: str
    capabilities: tuple[Capability, ...]
    cancelled: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Sequence:
    """The order milestones run in, and the bare name of the document declaring it."""

    name: str
    milestones: tuple[str, ...]


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


def _declaration(lines: list[str], start: int) -> str | None:
    """Find the declaration line following the heading at `start`, if any."""
    for line in lines[start + 1 : start + 1 + _LOOKAHEAD]:
        if not line.strip():
            continue
        return line if _DECLARATION.match(line) else None
    return None


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
    """
    _citable(name)
    lines = text.splitlines()
    titled = next((_AREA.match(line) for line in lines if _AREA.match(line)), None)
    if titled is None:
        raise IndexRefused(f"{name}: no `# E<nn> — <area>` title, so its rows have no area")
    epic, area = titled.group(1), _clean(titled.group(2))

    found: list[Capability] = []
    cancelled: list[str] = []
    for position, line in enumerate(lines):
        if not _ANY_HEADING.match(line):
            continue
        declaration = _declaration(lines, position)
        if declaration is None:
            continue
        heading = _HEADING.match(line)
        if heading is None:
            raise IndexRefused(
                f"{name} line {position + 1}: a task heading declares a milestone and "
                "carries no id. ⛔ The line is not quoted: it is caller text"
            )
        milestone = _MILESTONE.match(declaration)
        if milestone is None:
            raise IndexRefused(
                f"{name} line {position + 1}: {heading.group(1)} declares a milestone that is "
                "neither `M<n>` nor a dash — refused, never counted as cancelled (W247)"
            )
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
            )
        )
    return Epic(epic=epic, area=area, capabilities=tuple(found), cancelled=tuple(cancelled))


@dataclass(frozen=True, slots=True)
class Index:
    """Every capability the framework will have, ordered by when it lands."""

    epics: tuple[Epic, ...]
    sequence: Sequence

    @classmethod
    def of(cls, epics: Iterable[Epic], sequence: Sequence) -> Index:
        """Build an index, refusing a duplicate id or a milestone the order omits.

        ⛔ `sequence` is required: an index with no declared order would fall
        back to id order without saying so, which is the defect it removes.
        """
        gathered = tuple(epics)
        if not gathered:
            raise IndexRefused("an index of no epics answers every question with silence")
        seen: dict[str, str] = {}
        for epic in gathered:
            for capability in epic.capabilities:
                if capability.id in seen:
                    raise IndexRefused(
                        f"{capability.id} is declared twice — in {seen[capability.id]} "
                        f"and in {epic.epic}"
                    )
                if capability.milestone not in sequence.milestones:
                    raise IndexRefused(
                        f"{capability.id} lands at {capability.milestone}, which "
                        f"{sequence.name} does not declare, so it has no place in the order"
                    )
                seen[capability.id] = epic.epic
        return cls(gathered, sequence)

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        """Every capability, in the order the documents declared them."""
        return tuple(c for epic in self.epics for c in epic.capabilities)

    @property
    def cancelled(self) -> tuple[str, ...]:
        """Every row that declares no milestone, counted rather than dropped."""
        return tuple(name for epic in self.epics for name in epic.cancelled)

    @property
    def milestones(self) -> tuple[str, ...]:
        """Every declared milestone, in the declared order — ⛔ empty ones included."""
        return self.sequence.milestones

    def milestone_of(self, task: str) -> str:
        """When `task` lands. ⛔ Refuses an id the index does not carry."""
        for capability in self.capabilities:
            if capability.id == task:
                return capability.milestone
        raise IndexRefused(f"no such capability — the index carries {len(self.capabilities)}")

    def _position(self, milestone: str) -> int:
        """Say where `milestone` falls in the declared order, refusing one it omits."""
        if milestone not in self.milestones:
            raise IndexRefused(f"no such milestone — the index knows {self.milestones}")
        return self.milestones.index(milestone)

    def later(self, milestone: str, *, than: str) -> bool:
        """Say whether `milestone` comes strictly after `than` in the declared order.

        ⛔ **The one comparison of milestones in this package.** Anything that
        asks *is this later?* asks here, so no caller can compare ids instead.
        """
        return self._position(milestone) > self._position(than)

    def at(self, milestone: str) -> tuple[Capability, ...]:
        """Every capability delivered at `milestone`, in document order."""
        return tuple(c for c in self.capabilities if c.milestone == milestone)

    def after(self, milestone: str) -> tuple[Capability, ...]:
        """Every capability delivered strictly later than `milestone`.

        ⭐ This is what a corpus that finishes at `milestone` will never use,
        and it is the population a terminal statement has to account for.
        """
        self._position(milestone)
        return tuple(c for c in self.capabilities if self.later(c.milestone, than=milestone))

    def render(self) -> str:
        """Render the index as a document, byte-identical on every regeneration."""
        out = [
            "# The capability index",
            "",
            f"**{BANNER}**",
            "",
            "⭐ **What a planner asks the framework, and the only thing it has to "
            "read to find out: *when does capability X become available?***",
            "",
            "⛔ **Derived from the epic documents, never transcribed from them.** "
            "A hand-edit here is a finding against the delivery skill (R19), not "
            "a fix — it is reverted by the next regeneration.",
            "",
            self._derivation(),
            "",
            f"⛔ **Milestones run in the order `{self.sequence.name}` declares, not the "
            f"order their ids sort to:** {' → '.join(f'`{m}`' for m in self.milestones)}.",
            "",
        ]
        for milestone in self.milestones:
            delivered = self.at(milestone)
            counted = "capability" if len(delivered) == 1 else "capabilities"
            out += [f"## {milestone} — {len(delivered)} {counted}", ""]
            if not delivered:
                out += [EMPTY, ""]
                continue
            out += [
                "| capability | what it is | area | waits on |",
                "|---|---|---|---|",
                *(c.row() for c in delivered),
                "",
            ]
        return "\n".join(out)

    def _derivation(self) -> str:
        """Derive the coverage line — ⛔ never a literal somebody typed."""
        dropped = len(self.cancelled)
        empty = sum(1 for milestone in self.milestones if not self.at(milestone))
        return (
            f"**{len(self.capabilities)} capabilities · {len(self.epics)} epic documents · "
            f"{len(self.milestones)} milestones, {empty} with no capability · {dropped} "
            f"cancelled {'row' if dropped == 1 else 'rows'} carried and not counted.**"
        )
