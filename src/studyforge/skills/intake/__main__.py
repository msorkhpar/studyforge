"""`python3 -m studyforge.skills.intake check|render|questions`: the intake command line.

`check [BRIEF]` prints each open finding, then `open: N`, and exits 1 when N is above 0.
`render [BRIEF]` writes `brief.md` beside the brief. `questions [--track T]` lists the
questions a track asks. Every failure prints one line to stderr and exits 2; messages never
repeat what a brief contains.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from . import BANK, BRIEF_PATH, TRACKS, BriefError, check, load, render

USAGE = ("usage: python3 -m studyforge.skills.intake check [BRIEF] | render [BRIEF] "
         "| questions [--track T]")


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def _private_ignored(root: Path) -> bool:
    """Ask git whether `.private/` is ignored; raise OSError with a one-line reason."""
    argv = ["git", "-C", str(root), "check-ignore", "-q", ".private/"]
    try:
        code = subprocess.run(argv, capture_output=True, check=False).returncode
    except OSError:
        raise OSError("git is not available to judge .private/") from None
    if code not in (0, 1):
        raise OSError(f"{root}: git cannot judge .private/ (is it a git repository?)")
    return code == 0


def _check(path: Path) -> int:
    brief = load(path)
    ignored = _private_ignored(path.resolve().parent.parent)
    findings = check(brief, private_ignored=ignored)
    for line in findings:
        print(line)
    print(f"open: {len(findings)}")
    return 1 if findings else 0


def _render(path: Path) -> int:
    brief = load(path)
    target = path.parent / "brief.md"
    try:
        target.write_text(render(brief), encoding="utf-8", newline="\n")
    except OSError:
        raise OSError(f"{target}: cannot write") from None
    try:
        print(target.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        print(target)
    return 0


def _questions(track: str | None) -> int:
    tracks = (track,) if track else TRACKS
    for name in tracks:
        if track is None:
            print(f"== {name} ==")
        for question in BANK:
            if name in question.tracks:
                print(f"{question.id} [{question.tier}] {question.ask}")
                print(f"  why: {question.why}")
                print(f"  default: {question.default}")
    return 0


def main(argv: list[str]) -> int:
    """Run one verb; return the process exit status."""
    verb, rest = (argv[0], argv[1:]) if argv else ("", [])
    try:
        if verb in ("check", "render") and len(rest) <= 1:
            path = Path(rest[0] if rest else BRIEF_PATH)
            return _check(path) if verb == "check" else _render(path)
        if verb == "questions" and rest == []:
            return _questions(None)
        if verb == "questions" and len(rest) == 2 and rest[0] == "--track":
            return _questions(rest[1]) if rest[1] in TRACKS else _fail(USAGE)
    except (BriefError, OSError) as err:
        return _fail(str(err))
    return _fail(USAGE)


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
