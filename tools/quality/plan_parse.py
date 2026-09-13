"""The plan's texts, parsed: epic rows, the README's steps and legend, `workspace.json`'s pins.

**What it does.** Answers what the plan's texts DECLARE, with no verdict: each capability row
of an epic document (`declarations`, `rows`), the step each id is placed in (`placement`), the
README's shorthand legend (`aliases`), the sibling components `workspace.json` pins
(`components`), an epic preamble's component (`preamble_component`), and the components a
cell's code spans reach (`resolve`). ⛔ `creators` judges what it returns (`W285`).

**How you use it.** Through `tools.quality.creators`, which re-exports each name a reader
imports. Every function is handed text, so a historical ref is read with `git show`.

**Depends on.** `json`, `re` and `dataclasses`; `config` for `ROW_ID`, `markdown` for the
code-span grammar, `report` for a refused row's `Finding`. ⛔ Never `creators`.

## ⚠️ WHAT IT DECIDES, AND WHAT IT DECLARES (Ruling 292)

⭐ **Decided:**

- a MILESTONE is a whole `MILESTONE_ID` or the cancelling dash. ⛔ Else it is refused by name as
  `milestone-id` (`W275`). `src/` cannot export the shape to `tools/`, so it is typed once, here.

⚠️ **Declared:** a step line is `- **<n>.<n>** — …`, with code spans and parentheses
blanked. An id is placed by the FIRST step line naming it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from tools.quality.config import ROW_ID
from tools.quality.markdown import code_spans, strip_code_spans
from tools.quality.report import Finding

RULE_MILESTONE = "milestone-id"
TASKS_DIR = "docs/tasks"
SEQUENCE = f"{TASKS_DIR}/README.md"
WORKSPACE = "workspace.json"
OWNS = "Owns"
CONTEXT = "Context"

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
