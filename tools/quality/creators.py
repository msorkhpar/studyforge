"""`W156`: a row may not `Own` inside a component whose creator it cannot be shown to follow.

**What it does.** Reads the plan's graph: every capability row in the epic documents, its
`Owns` and `Context` cells and its `Depends on` line, the step `docs/tasks/README.md` places
it in, and the sibling components `workspace.json` pins. Of each row that owns INSIDE a
sibling component it does not create, it asks two things. Does the row's declared
`Depends on` chain reach the component's creator? Does the creator sit in the same step or
an earlier one? ⛔ A member failing either is a finding: a dispatcher obeying the README's
corrected rule (in-step edges are read off the epic) puts it in flight with nowhere to write.

**How you use it.** `check_owns_before_creator(root)` is registered in `CHECKS`, and
`creator_census(root)` in `NOTICES`. The census prints every member with its creator, its
verdict and HOW its component was derived, so a green exit carries its population.
`graph(sequence, workspace, epics)` is the pure reading both are built on. It is handed
text, so a historical ref can be read with `git show` and no tree export.

**Depends on.** `json`, `math`, `re`, `dataclasses` and `pathlib`; `config` for `ROW_ID`
and `read_text`, `markdown` for the code-span grammar, `report` for the answer.

## ⚠️ WHAT IT DECIDES, AND WHAT IT DECLARES (Ruling 292)

⭐ **Decided:**

- a COMPONENT is a `workspace.json` component whose `where` is not `self`. A code span
  reaches one through the README's shorthand legend (`TC/` = `code-server-toolchain`) or by
  its own name;
- a CREATOR claim is an `Owns` code span naming a component's ROOT (`TC/`,
  `narrate-service`). The creator is the claimant placed EARLIEST in the README's step lines,
  read in document order, which is the decided milestone order. Every other row owning inside
  the component is a MEMBER, a later root claimant included;
- a MILESTONE is a whole `MILESTONE_ID` or the cancelling dash. ⛔ Else it is refused by name as
  `milestone-id` (`W275`). `src/` cannot export the shape to `tools/`, so it is typed once, here;
- the EDGE is the transitive closure of `Depends on`: `TC-05` reaches `TC-01` through `TC-02`;
- ⛔ **an EARLIER-step creator with no edge is a finding as well.** The README's widened rule
  lets a later step START once an earlier one is saturated, so step order alone no longer
  proves the creator lands first. Only the edge does.

⚠️ **Declared, and each is printed or asserted rather than smoothed:**

1. an `Owns` cell with NO code span at all is resolved from its epic's PREAMBLE, the one bold
   code span there that names a component. The census prints it as `prose`, the weak derivation;
2. a component no row claims to create is pre-existing where `workspace.json` pins it
   `present`, and is not walked. Anywhere else it is a finding;
3. a row the README places in no step is judged on its edge alone;
4. `Context` READS are a second arm, printed and never failing the floor. Only a code span is
   read there, so *"the narration service's equivalent"* is prose nothing resolves;
5. a step line is `- **<n>.<n>** — …`, with code spans and parentheses blanked. An id is
   placed by the FIRST step line naming it.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from tools.quality.config import ROW_ID, read_text
from tools.quality.markdown import code_spans, strip_code_spans
from tools.quality.report import Finding

RULE_CREATOR = "owns-before-creator"
RULE_MILESTONE = "milestone-id"
TASKS_DIR = "docs/tasks"
SEQUENCE = f"{TASKS_DIR}/README.md"
WORKSPACE = "workspace.json"
SOUND = "sound"
OWNS = "Owns"
CONTEXT = "Context"
PATH = "path"
PROSE = "prose"

_HEADING = re.compile(r"^###\s+([A-Z]{2,4}-[0-9]{1,3}[a-z]?)\s+—")
_DECLARATION = re.compile(r"^\*\*Milestone\*\*")
#: ⛔ THE milestone id in `tools/`, whole and any width (`W275`): `M1x` once read as `M1`.
MILESTONE_ID = r"M[0-9]+"
#: The milestone a declaration carries — a whole id, or the dash that cancels — allowing the bold.
_MILESTONE = re.compile(rf"^\*\*Milestone\*\*\s*\**\s*({MILESTONE_ID}\b|—)")
#: It names the row and never quotes the declaration, as `W247` refuses in `capability.py`.
_REFUSED = (
    "{} declares a milestone that is neither a whole `M<digits>` id nor the dash that cancels, "
    "so it is neither read as a row nor counted cancelled. Write the id whole (W275)"
)
_DEPENDS = re.compile(r"\*\*Depends on\*\*\s*(.*?)(?:·|$)")
_STEP = re.compile(r"^- \*\*([0-9]+\.[0-9]+)\*\*\s+—\s+(.*)$")
_LEGEND = re.compile(r"`([A-Za-z]+)/`\s*=\s*`([^`/]+)")
_BOLD_SPAN = re.compile(r"\*\*`([^`]+)`\*\*")
_PARENTHESES = re.compile(r"\([^)]*\)")
_FIELD = re.compile(r"\*\*(Owns|Context)\*\*")
_LOOKAHEAD = 3


@dataclass(frozen=True)
class Row:
    """One capability row: where it is written, what it owns and reads, what it waits on."""

    id: str
    document: str
    line: int
    owns: str
    context: str
    depends: tuple[str, ...]


@dataclass(frozen=True)
class Member:
    """A row reaching inside a component it does not create, and the verdict on it."""

    row: Row
    component: str
    arm: str
    derivation: str
    creator: Row | None
    verdict: str


@dataclass(frozen=True)
class Graph:
    """The plan as this predicate reads it, with the population a census prints."""

    rows: tuple[Row, ...]
    documents: int
    steps: dict[str, str]
    creators: dict[str, Row]
    members: tuple[Member, ...]
    refused: tuple[Finding, ...]


def components(workspace: str) -> dict[str, str]:
    """Every sibling component `workspace.json` pins, mapped to its status."""
    try:
        data = json.loads(workspace)
    except ValueError:
        return {}
    entries = data.get("components", []) if isinstance(data, dict) else []
    return {
        entry["name"]: str(entry.get("status", ""))
        for entry in entries
        if isinstance(entry, dict) and "name" in entry and entry.get("where") != "self"
    }


def aliases(sequence: str, names: set[str]) -> dict[str, str]:
    """Return the README legend's shorthand, kept where it names a sibling component."""
    return {alias: target for alias, target in _LEGEND.findall(sequence) if target in names}


def placement(sequence: str) -> dict[str, str]:
    """Each capability id mapped to the FIRST step line naming it."""
    steps: dict[str, str] = {}
    for line in sequence.splitlines():
        match = _STEP.match(line)
        if match is None:
            continue
        body = _PARENTHESES.sub(" ", strip_code_spans(match.group(2)))
        for found in ROW_ID.findall(body):
            if "-" in found:
                steps.setdefault(found, match.group(1))
    return steps


def rows(document: str, text: str) -> list[Row]:
    """Every capability row in one epic document; a cancelled row (milestone `—`) is not one."""
    return declarations(document, text)[0]


def declarations(document: str, text: str) -> tuple[list[Row], list[Finding]]:
    """Return one epic document's rows, and a finding per milestone it refuses (`W275`)."""
    lines = text.splitlines()
    found: list[Row] = []
    refused: list[Finding] = []
    for position, line in enumerate(lines):
        heading = _HEADING.match(line)
        if heading is None:
            continue
        block = _block(lines, position)
        milestone = _MILESTONE.match(block[0]) if block else None
        if block and milestone is None:
            name = _REFUSED.format(heading.group(1))
            refused.append(Finding(document, position + 1, RULE_MILESTONE, name))
        if milestone is None or milestone.group(1) == "—":
            continue
        cells = dict.fromkeys((OWNS, CONTEXT), "")
        parts = _FIELD.split(" ".join(block))
        for name, value in zip(parts[1::2], parts[2::2], strict=True):
            cells[name] = value.strip()
        depends = _DEPENDS.search(block[0])
        waits = depends.group(1).replace("*", "").split(",") if depends else []
        found.append(
            Row(
                id=heading.group(1),
                document=document,
                line=position + 1,
                owns=cells[OWNS],
                context=cells[CONTEXT],
                depends=tuple(name.strip() for name in waits if name.strip() not in ("", "—")),
            )
        )
    return found, refused


def _block(lines: list[str], start: int) -> list[str]:
    """Return the declaration line after a heading and every line up to the next blank one."""
    for offset, line in enumerate(lines[start + 1 : start + 1 + _LOOKAHEAD], start + 1):
        if not line.strip():
            continue
        if not _DECLARATION.match(line):
            return []
        block = []
        for following in lines[offset:]:
            if not following.strip():
                break
            block.append(following)
        return block
    return []


def preamble_component(text: str, names: set[str]) -> str | None:
    """Return the component an epic's preamble declares in bold code, if exactly one."""
    preamble = text.split("\n### ", 1)[0]
    declared = {name for name in _BOLD_SPAN.findall(preamble) if name in names}
    return declared.pop() if len(declared) == 1 else None


def _reached(body: str, shorthand: dict[str, str], names: set[str]) -> tuple[str | None, bool]:
    """Return the component one code span reaches, and whether the span is its ROOT."""
    span = body.strip()
    head, slash, rest = span.partition("/")
    if slash and head in shorthand:
        return shorthand[head], not rest
    if head in names:
        return head, not rest
    return None, False


def resolve(cell: str, shorthand: dict[str, str], names: set[str]) -> dict[str, bool]:
    """Every component a cell's code spans reach, mapped to whether one span names its ROOT."""
    reached: dict[str, bool] = {}
    for _, _, body in code_spans(cell):
        component, root = _reached(body, shorthand, names)
        if component is not None:
            reached[component] = reached.get(component, False) or root
    return reached


def graph(sequence: str, workspace: str, epics: dict[str, str]) -> Graph:
    """Read the plan from its three kinds of text into rows, creators and members."""
    pinned = components(workspace)
    names = set(pinned)
    shorthand = aliases(sequence, names)
    steps = placement(sequence)
    order = {step: index for index, step in enumerate(dict.fromkeys(steps.values()))}
    everything: list[Row] = []
    owned: list[tuple[Row, dict[str, bool], str]] = []
    refused: list[Finding] = []
    for document, text in epics.items():
        fallback = preamble_component(text, names)
        found, unreadable = declarations(document, text)
        refused.extend(unreadable)
        for row in found:
            everything.append(row)
            reached = resolve(row.owns, shorthand, names)
            if reached or code_spans(row.owns) or fallback is None:
                owned.append((row, reached, PATH))
            else:
                owned.append((row, {fallback: False}, PROSE))

    def rank(row: Row) -> float:
        return order.get(steps.get(row.id, ""), math.inf)

    creators: dict[str, Row] = {}
    for row, reached, _ in owned:
        for component, root in reached.items():
            if root and (component not in creators or rank(row) < rank(creators[component])):
                creators[component] = row

    edges = {row.id: row.depends for row in everything}
    members: list[Member] = []
    arms = [(OWNS, row, reached, how) for row, reached, how in owned]
    arms += [(CONTEXT, row, resolve(row.context, shorthand, names), PATH) for row in everything]
    for arm, row, reached, how in arms:
        for component in reached:
            creator = creators.get(component)
            if creator is not None and creator.id == row.id:
                continue
            if creator is None and pinned.get(component) == "present":
                continue
            verdict = _verdict(row, creator, rank, edges)
            members.append(Member(row, component, arm, how, creator, verdict))
    return Graph(tuple(everything), len(epics), steps, creators, tuple(members), tuple(refused))


def _closure(start: str, edges: dict[str, tuple[str, ...]]) -> set[str]:
    """Every id `start` waits on, directly or through another row."""
    seen: set[str] = set()
    pending = list(edges.get(start, ()))
    while pending:
        name = pending.pop()
        if name not in seen:
            seen.add(name)
            pending.extend(edges.get(name, ()))
    return seen


def _verdict(row: Row, creator: Row | None, rank, edges: dict[str, tuple[str, ...]]) -> str:
    """`SOUND`, or the reason this member can be dispatched before its creator lands."""
    if creator is None:
        return "no row creates it and workspace.json does not pin it present"
    mine, theirs = rank(row), rank(creator)
    if theirs > mine and not math.isinf(theirs):
        return f"its creator {creator.id} is placed in a LATER step"
    if creator.id in _closure(row.id, edges):
        return SOUND
    if math.inf in (mine, theirs):
        relation = "one of the two is placed in no step"
    else:
        relation = "the SAME step" if theirs == mine else "an EARLIER step, which proves no order"
    return f"no declared Depends on chain reaches its creator {creator.id} ({relation})"


def read(root: Path) -> Graph | None:
    """Return the live plan under `root`, or None when it has no README or workspace pin."""
    sequence = read_text(root / SEQUENCE) if (root / SEQUENCE).is_file() else None
    workspace = read_text(root / WORKSPACE) if (root / WORKSPACE).is_file() else None
    if sequence is None or workspace is None:
        return None
    epics = {
        f"{TASKS_DIR}/{path.name}": read_text(path) or ""
        for path in sorted((root / TASKS_DIR).glob("E[0-9]*.md"))
    }
    return graph(sequence, workspace, epics)


def check_owns_before_creator(root: Path) -> list[Finding]:
    """One finding per refused milestone, and per `Owns` member not shown to follow its creator."""
    plan = read(root)
    if plan is None:
        return []
    return list(plan.refused) + [
        Finding(
            member.row.document,
            member.row.line,
            RULE_CREATOR,
            f"{member.row.id} Owns inside `{member.component}` ({member.derivation}) and "
            f"{member.verdict}. Declare the edge in its Depends on line, or re-point its "
            "Owns at a path that exists before the creator runs (W156)",
        )
        for member in plan.members
        if member.arm == OWNS and member.verdict != SOUND
    ]


def creator_census(root: Path) -> list[str]:
    """Print the walked population, every member and its verdict, green run or red."""
    plan = read(root)
    if plan is None:
        return [
            f"owns before creator (W156): not read, no {SEQUENCE} or {WORKSPACE} under this "
            "root, so no row was walked"
        ]
    owners = [member for member in plan.members if member.arm == OWNS]
    placed = sum(1 for row in plan.rows if row.id in plan.steps)
    lines = [
        f"owns before creator (W156): {len(plan.rows)} capability rows in {plan.documents} "
        f"epic documents, {placed} placed in a step; {len(plan.creators)} components created "
        f"by a row; {len(owners)} Owns members, "
        f"{sum(1 for member in owners if member.derivation == PROSE)} read from epic prose, "
        f"{sum(1 for member in owners if member.verdict != SOUND)} unsound. A component no "
        "row creates and workspace.json pins present is not walked."
    ]
    for component, creator in sorted(plan.creators.items()):
        step = plan.steps.get(creator.id, "no step")
        lines.append(f"  {component}: created by {creator.id} ({step})")
    for member in sorted(plan.members, key=lambda item: (item.arm != OWNS, item.row.id)):
        step = plan.steps.get(member.row.id, "no step")
        lines.append(
            f"    {member.row.id} {member.arm} {member.derivation} inside {member.component}"
            f", {step}: {member.verdict}"
            + (" (a read: printed, never a finding)" if member.arm == CONTEXT else "")
        )
    return lines


__all__ = [
    "MILESTONE_ID",
    "RULE_CREATOR",
    "RULE_MILESTONE",
    "Graph",
    "Member",
    "Row",
    "check_owns_before_creator",
    "creator_census",
    "declarations",
    "graph",
    "placement",
    "read",
    "resolve",
    "rows",
]
