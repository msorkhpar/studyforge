"""Shared machinery for `tools/tests/quality/board/` — ⛔ the FOUNDING BYTES, in one place.

⛔ **These tables are not invented: they are the MEASURED FAILURES, replayed from
their own bytes**, each quoted with the ref it was taken at (Ruling 97's standing
rule). ⭐ **They live here rather than in one test module because `W111` split
`observation.py` at the `W96/3` seam and both halves are asserted against the same
population** — ⚠️ **and a fixture copied into two modules is a fact with two homes,
which is the defect `board.md` exists to forbid, one layer down.**

| Replay | The bytes | Taken at |
|---|---|---|
| 350 commits | `W14`+`W18` and `W27`, `none` / `0` / started | `cae114e^` |
| bidirectional | `SF-34` and `W85`+`W86`+`W87`, a checkout that had gone | `679a6c5^` |
| the Checkout cell | `SF-15` and `W95`, a checkout and `0` ahead — ⭐ **a PASS** | `7559398` |

⭐ **The third is the CONTROL and it is the one that constrains the predicate:**
⛔ **both its rows pass on the `Checkout` cell and NOT on `ahead`**, so no single
cell is the rule and a predicate demanding `ahead > 0` would have flagged the two
rows that were correct (Ruling 130, and Ruling 179's cost).
"""

from __future__ import annotations

from tools.quality.board.observation import INFLIGHT_CLOSE, INFLIGHT_OPEN
from tools.quality.report import Finding

#: The observation table's header, verbatim from every In-flight table this board
#: has carried. ⛔ Written out rather than generated: the header is the
#: DECLARATION the locator reads, and a paraphrase would test a shape the board
#: does not author.
HEADER = "| Row | Owner | Checkout | Commits ahead | State |\n|---|---|---|---|---|\n"

#: ⛔ **A header that declares NONE of the three roles** — the CTO's round-50 plant,
#: which is `W111`'s whole subject: two column names renamed inside a table that is
#: still a table. ⚠️ **It must be refused INSIDE the markers and invisible OUTSIDE
#: them**, and those are different assertions.
RENAMED = "| Row | Owner | Where | Commits on it | Phase |\n|---|---|---|---|---|\n"

#: ⛔ **`cae114e^`, and these two lines are this package's founding bytes.**
THREE_HUNDRED_AND_FIFTY = (
    "| `W14` + `W18` | Developer 1 | none | 0 | in flight |\n"
    "| `W27` | Developer 2 | none | 0 | ◐ in-review @ `655b527` |\n"
)

#: ⛔ **`7559398`, and it must PASS** — a checkout and `0` commits ahead.
THE_CHECKOUT_CELL = (
    "| `SF-15` | Developer 1 | `wt/dev1`, `feat/SF-15-contents` | 0 | in flight |\n"
    "| `W95` | Developer 2 | `wt/dev2`, `fix/W95-shared-origin-fixture` | 0 | in flight |\n"
)

#: ⛔ **`679a6c5^`, the bidirectional wave** — ⚠️ **both cells CLAIM a checkout that
#: had gone, so this table is a PASS for the floor rules and is refuted only by
#: `corroborate.py`.**
BIDIRECTIONAL = (
    "| `SF-34` | Developer 1 | `wt/dev1`, `feat/SF-34-chrome` | 0 | in flight |\n"
    "| `W85` + `W86` + `W87` | Developer 2 | `wt/dev2`, `fix/board-instrument` | **+1** "
    "| in-review |\n"
)

REGISTER = "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
REGISTER_END = "<!-- /register -->\n"


def board(
    observation: str = "",
    register: str = "",
    delimited: bool = False,
    header: str = HEADER,
) -> str:
    """A board with a register and, optionally, a delimited observation table.

    ⚠️ **`delimited=False` is now the Ruling 196(b) RAMP and nothing else** — a board
    carrying no marker at all — ⭐ which is the only shape the header locator still
    answers for after `W111`.
    """
    table = ""
    if observation or (delimited and header):
        table = header + observation
        if delimited:
            table = f"{INFLIGHT_OPEN}\n{table}{INFLIGHT_CLOSE}\n"
    return f"# Board\n\n## In flight\n\n{table}\n{REGISTER}{register}{REGISTER_END}"


def rules(findings: list[Finding]) -> list[str]:
    """The rule codes of `findings`, sorted, so a reading is compared as a SET of rules."""
    return sorted(finding.rule for finding in findings)
