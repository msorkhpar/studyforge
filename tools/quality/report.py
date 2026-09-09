"""What a failed check says, and how it is printed.

**What it does.** Gives the four checks one shape of answer — a `Finding` —
and one way of rendering it, so a failure names a rule, a file and a line
whatever produced it (R6: fail loud, by name).

**How you use it.** A check returns `list[Finding]`; a caller renders them
with `format_findings`. Nothing else here.

**Depends on.** `dataclasses` only.
"""

from __future__ import annotations

from dataclasses import dataclass


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
