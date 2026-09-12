"""What a check says, what a notice counts, and how either is printed.

**What it does.** Gives the floor's two channels one shape of answer each — a
`Finding` for a violation, and a `DocumentPopulation` for the denominator a
notice prints beside a scalar — plus one way of rendering a finding, so a
failure names a rule, a file and a line whatever produced it (R6: fail loud,
by name).

**How you use it.** A check returns `list[Finding]`; a caller renders them
with `format_findings`. A walk that a figure will be quoted over returns a
`DocumentPopulation`, and the notice quoting that figure names its `walk` and
appends `WALK_CAVEAT[walk]` (`W148`).

**Depends on.** `dataclasses` and `pathlib` — standard library. ⚠️ This line
read *"`dataclasses` only"* until `W148` gave a population a type.
"""

from __future__ import annotations

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
    """The documents a figure is taken over, and which walk produced them."""

    paths: tuple[Path, ...]
    walk: str


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
