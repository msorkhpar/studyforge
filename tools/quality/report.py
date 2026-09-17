"""What a check says, what a notice counts, and how either is printed.

**What it does.** Gives the floor's two channels one shape of answer each — a
`Finding` for a violation, and a `DocumentPopulation` for the denominator a
notice prints beside a scalar — plus one way of rendering a finding, so a
failure names a rule, a file and a line whatever produced it (R6: fail loud,
by name).

**How you use it.** A check returns `list[Finding]`; a caller renders them
with `format_findings`. A walk that a figure will be quoted over returns a
`DocumentPopulation`, and the notice quoting that figure names its `walk` and
appends `WALK_CAVEAT[walk]` (`W148`) and `unread_caveat(population)` (`W315`,
for `W232/5`) — ⛔ **the first says how the population was found, the second
says what it did not find**, and a reader believing a green over an unstaged
document needs the second. A test run's summary prints
`unreachable_population(stats)` — the tests it skipped, counted and grouped by
the reason each skip gave (`W158`).

**Depends on.** `collections`, `dataclasses` and `pathlib` — standard library. ⚠️ This line
read *"`dataclasses` only"* until `W148` gave a population a type.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

#: ⛔ **How a document population was derived, NAMED in every figure taken over
#: it** (`W148`). Two named walks and never a boolean: `W148`'s whole cost was
#: two offices at ONE ref printing different figures with nothing in either
#: reading naming the cause.
TRACKED_WALK = "tracked"
DISK_WALK = "disk"

#: ⚠️ Appended to a figure taken over `DISK_WALK`, and EMPTY for the other one.
#: Ruling 216's third answer wearing a sentence: git failing to answer may
#: neither fall through to the disk in silence nor fail the build, so the
#: figure says which walk produced it and what that costs the reader.
WALK_CAVEAT = {
    TRACKED_WALK: "",
    DISK_WALK: (
        " ⚠️ This population came off the DISK — git named no tracked set here — so it "
        "carries untracked files and is not reproducible from another checkout."
    ),
}


@dataclass(frozen=True)
class DocumentPopulation:
    """The documents a figure is taken over, which walk produced them, and what it MISSED.

    ⛔ **`unread` is the count of markdown documents on the disk that the walk
    did NOT read**, and it is `0` by construction on `DISK_WALK`, where git
    named no tracked set and nothing was narrowed away. ⭐ **It exists because
    a narrowed population is silent about what it narrowed off** (`W232/5`):
    an office running the floor over a handoff it has written but not staged
    gets a green that the merge will not repeat, and no figure said so.
    """

    paths: tuple[Path, ...]
    walk: str
    unread: int = 0


def unread_caveat(population: DocumentPopulation) -> str:
    """Return the sentence a TRACKED figure owes about what its walk did NOT read.

    ⛔ **Printed whether or not it fired** (Ruling 48): `0 documents unindexed`
    is the reading an office needs before it believes a green over its own
    work, and it is exactly the reading a fired-only sentence would never give.
    ⚠️ **Empty on `DISK_WALK`**, where `WALK_CAVEAT` already says the
    population carries untracked files and where a `0` here would claim git
    had answered.
    """
    if population.walk != TRACKED_WALK:
        return ""
    return (
        f" ⚠️ {population.unread} markdown documents in this working tree are absent from "
        f"git's INDEX and were NOT read here (`W232/5`): a document written and not "
        f"`git add`ed gets a reading the merge will not repeat."
    )


@dataclass(frozen=True, order=True)
class Finding:
    """One violation of the quality floor.

    `path` is repo-relative with forward slashes — ⛔ never absolute, because
    an absolute path in a build log carries the user's home directory (R7).
    `line` is 1-based, or 0 when the finding is about the file as a whole
    (a missing test mirror has no line to point at).
    """

    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        """`path:line: [rule] message`, the shape an editor can jump to."""
        return f"{self.path}:{self.line}: [{self.rule}] {self.message}"


def format_findings(findings: list[Finding]) -> str:
    """Every finding on its own line, sorted, with a count.

    Sorted rather than in discovery order so that the same repository produces
    the same report on any machine — the same argument as R10, applied to the
    tool that guards it.
    """
    if not findings:
        return "quality floor: clean"
    lines = [str(finding) for finding in sorted(findings)]
    noun = "finding" if len(lines) == 1 else "findings"
    lines.append(f"quality floor: {len(lines)} {noun}")
    return "\n".join(lines)


#: ⛔ **The label every test run prints, reached or not** (`W158`). ⚠️ Printed on
#: an EMPTY population too: `green` with nothing skipped and `green` with a hole
#: are two answers, and only a line present in BOTH tells them apart (Ruling 191).
UNREACHABLE = "unreachable population"

#: What pytest prefixes to a skip's own reason, dropped so the reason reads as typed.
SKIP_PREFIX = "Skipped: "


def skip_reason(report: object) -> str:
    """Return the reason a skipped report gave, as its author wrote it.

    ⭐ Read off pytest's `longrepr` — `(path, line, "Skipped: reason")` for a skip —
    and never matched against a list: a reason no list anticipated still prints.
    """
    longrepr = getattr(report, "longrepr", None)
    text = longrepr[2] if isinstance(longrepr, tuple) and len(longrepr) == 3 else longrepr
    reason = str(text or "no reason given")
    return reason.removeprefix(SKIP_PREFIX)


def unreachable_population(stats: dict) -> list[str]:
    """Return the tests this run did not reach, as a COUNT and each REASON (`W158`).

    ⛔ **Derived from the run's own tally** (`terminalreporter.stats`), never typed:
    a test count, one per skipped report, as pytest's closing line counts them.
    ⛔ **A disclosure and never a verdict** (Ruling 328) — it returns lines and
    no exit code, because what is unreachable is host state no branch controls.
    """
    reasons = Counter(skip_reason(report) for report in stats.get("skipped", []))
    total = sum(reasons.values())
    if not total:
        return [f"{UNREACHABLE}: 0 skipped test(s) — this run reached every test it collected"]
    lines = [
        f"{UNREACHABLE}: {total} skipped test(s) — this run's green does not cover them "
        f"(a disclosure, never a failure)"
    ]
    for reason, count in sorted(reasons.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"  {count} × {reason}")
    return lines
