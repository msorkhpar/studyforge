r"""Reading the workspace's pin document, so the index can say **not this side**.

**What it does.** Reads which components this workspace places somewhere other
than here, and answers the one question the index asks of that reading:
⭐ **which side delivers a row** — one of three values and never a fourth.

**How you use it.**

    from studyforge.skills.delivery import Components

    components = Components.read(pins, order_text)   # both are TEXT
    components.side(capability.owns, epic.preamble)  # a value in `SIDES`
    Components.none()                                # nothing but this repository

**Depends on.** `re` and `dataclasses`. ⛔ Nothing else, ever — not this
package, not the filesystem: it is handed text and gives back data, so the
caller names the documents. ⛔ **And not `json`, deliberately** — see the note
on the pin document below.

## ⛔ Why there is a column for the side at all (`W92`)

⚠️ **The index had four columns and none of them said whose work a row is.**
A corpus that finishes at the reading floor has to account for every
capability delivered after it, and the table it writes asks *why this corpus
never reaches it* — ⛔ **which is a false question for a row delivered in
another repository entirely, and there was no field in which to say so.**

⭐ **It is the absence of a field, not a wrong value in one**, so no amount of
care at generation time could avoid the false statement. The remedy is the
field, and `terminal` is what stops asking once it exists.

## ⛔ The vocabulary is CLOSED, and it is a NARROWED population

⭐ **Three values and no others** (`SIDES`), each one a reading and never a
judgement:

| value | what was read |
|---|---|
| `HERE` | the row's `Owns` names a path, and it reaches no component pinned elsewhere |
| `ELSEWHERE` | that cell — or, when it names no path, its epic's preamble — reaches one |
| `UNDECLARED` | ⚠️ neither names one, so **nothing in the documents says** |

⛔ **`UNDECLARED` is not a soft `HERE`.** A row whose deliverable is a log, a
record or a skill declares no path at all, and guessing a side for it is
exactly the invention this column exists to remove. It is printed, so the hole
is visible and countable rather than smoothed into a column of confident
values.

## ⛔ No component is ever NAMED in what the index renders

⚠️ **The pin document's component names are read and never printed.** R1: the
framework knows nothing about any source, and a generated framework document
that named a corpus would be that knowledge written down. ⭐ The distinction a
planner needs is *structural* — this side or not this side — and the name adds
nothing to it.

## ⛔ The pin document is READ, never DECODED

⚠️ **`W7`'s coverage check makes a module that calls `json.loads` a reader of
somebody's document, and every such module must call the personal-data gate
(R7).** ⛔ This package may not: its contract is that it depends on nothing in
`corpus`, `archive` or `validate`, because a planner reasons about *work* and
not about a corpus's contents.

⭐ **So the pin document's components are read by pattern, not decoded.** What
is taken is two declared strings per entry and nothing else — no value from it
reaches an output, and no structure from it reaches a caller. ⚠️ A document
that does not carry that shape declares no component, and saying whether the
workspace's own pin file is well formed is the workspace check's question.

## ⛔ Why this is its own module, and it is NOT a third seam (`W92b`)

⭐ **There is one cut in this package's index half — READING versus BEING THE
INDEX** — and `W92` and `W94` each made it, naming the halves the other way
round. ⚠️ **Collapsed, that cut has two readers on its reading side:** `epics`
reads the epic documents and this module reads the pin document. ⛔ It sits
here rather than inside `capability` because it is a reader, which is the
existing seam's own answer — not because `capability` needed to be smaller.

⭐ **And it takes the two CELLS it reads, never a `Capability`**: a leaf that
imports nothing from this package cannot close a cycle with the module that
indexes it, and `refusal` is the same shape for the same reason.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: ⭐ The row is delivered in the repository this index is generated in.
HERE = "this framework"

#: ⭐ It is delivered inside a component the pin document places somewhere else.
ELSEWHERE = "⭐ not this framework"

#: ⚠️ Nothing in the documents says. ⛔ Never guessed into one of the other two.
UNDECLARED = "⚠️ undeclared"

#: ⛔ The whole vocabulary of the column, enumerated. A fourth value is a change
#: to this tuple and to the test that reads it, never a string somebody passes.
SIDES = (HERE, ELSEWHERE, UNDECLARED)

#: The column's heading, written once so the renderer and its test agree.
SIDE_COLUMN = "delivered in"

#: A code span. The `Owns` cell names its paths in these, and so does the
#: order document's shorthand legend.
_SPAN = re.compile(r"`([^`\n]+)`")

#: A **bold** code span, which is how an epic's preamble names its component.
_BOLD_SPAN = re.compile(r"\*\*`([^`\n]+)`\*\*")

#: The order document's shorthand legend: ``  `TC/` = `code-server-toolchain`  ``.
_LEGEND = re.compile(r"`([A-Za-z]+)/`\s*=\s*`([^`/\n]+)")

#: One entry of a pin document, and the two strings taken out of it. ⛔ Read by
#: pattern and never decoded, which is the note above and not an optimisation.
_PIN_ENTRY = re.compile(r"\{[^{}]*\}", re.S)
_PIN_NAME = re.compile(r'"name"\s*:\s*"([^"\n]+)"')
_PIN_WHERE = re.compile(r'"where"\s*:\s*"([^"\n]+)"')

#: What a pin document's `where` reads for the component it is written in.
#: ⛔ Everything else is somewhere else, whatever it is called.
SELF = "self"


@dataclass(frozen=True, slots=True)
class Components:
    """Every component the pin document places somewhere other than here."""

    names: frozenset[str]
    shorthand: dict[str, str] = field(default_factory=dict)

    @classmethod
    def none(cls) -> Components:
        """Declare that there is no component but this one.

        ⭐ The empty declaration, passed on purpose — the same shape
        `concentration(outside=())` requires, and for the same reason: a plan
        that never thought about the question must not read like one that did.
        """
        return cls(frozenset())

    @classmethod
    def read(cls, pins: str, order: str) -> Components:
        """Read the pin document's components, and the order document's shorthand.

        `pins` is the text of the document that pins this workspace's
        components; `order` is the text of the one that declares the milestone
        order, which is also where the shorthand legend lives. ⛔ Both are
        text: this module does not know where either document sits.

        ⚠️ A pin document that does not carry the declared shape names no
        component and is not refused here: this call answers *what is pinned*,
        and whether the workspace's own pin file is well formed is the
        workspace check's question, not the index's.
        """
        names = frozenset(
            found.group(1)
            for entry in _PIN_ENTRY.findall(pins)
            if (found := _PIN_NAME.search(entry))
            and (placed := _PIN_WHERE.search(entry))
            and placed.group(1) != SELF
        )
        legend = {alias: target for alias, target in _LEGEND.findall(order) if target in names}
        return cls(names, legend)

    def reaches(self, cell: str) -> bool:
        """Report whether any code span in `cell` names a path inside a component."""
        for body in _SPAN.findall(cell):
            head, slash, _ = body.strip().partition("/")
            if head in self.names or (slash and self.shorthand.get(head) in self.names):
                return True
        return False

    def declared_by(self, preamble: str) -> bool:
        """Report whether an epic's preamble names exactly one component, in bold code."""
        return len({name for name in _BOLD_SPAN.findall(preamble) if name in self.names}) == 1

    def side(self, owns: str, preamble: str) -> str:
        """Say which side delivers a row — ⛔ one of `SIDES`, never a fourth value.

        `owns` is the row's `Owns` cell verbatim and `preamble` its epic's, both
        as `epics` carried them. ⛔ The two CELLS and not the `Capability` they
        came off: this module holds the reading, and nothing of the vocabulary
        it is read into.
        """
        if self.reaches(owns):
            return ELSEWHERE
        if _SPAN.search(owns):
            return HERE
        return ELSEWHERE if self.declared_by(preamble) else UNDECLARED
